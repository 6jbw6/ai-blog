from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from app.core.database import get_db
from app.core.response import Result, PageResult, BusinessException
from app.api.deps import require_admin, get_optional_user
from app.models.article import Article
from app.models.tag import Tag
from app.models.article_tag import article_tags
from app.models.user import User
from app.schemas.article import ArticleCreate, ArticleUpdate, ArticleListItem, ArticleDetail
from app.ai_engine.rag_service import rag_service

router = APIRouter(prefix="/articles", tags=["文章管理 (Articles)"])


@router.get("", response_model=Result[PageResult[ArticleListItem]], summary="分页获取文章列表")
def list_articles(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    keyword: Optional[str] = None,
    category_id: Optional[int] = None,
    tag_id: Optional[int] = None,
    published_only: bool = True,
    db: Session = Depends(get_db)
):
    query = db.query(Article).options(
        joinedload(Article.category),
        joinedload(Article.tags),
        joinedload(Article.author)
    )

    if published_only:
        query = query.filter(Article.is_published == True)

    if category_id:
        query = query.filter(Article.category_id == category_id)

    if tag_id:
        query = query.join(Article.tags).filter(Tag.id == tag_id)

    if keyword:
        kw = f"%{keyword}%"
        query = query.filter(or_(Article.title.like(kw), Article.summary.like(kw), Article.content.like(kw)))

    total = query.distinct().count()
    
    # 置顶文章优先，其次按创建时间倒序
    articles = (
        query.order_by(Article.is_top.desc(), Article.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )

    items = [ArticleListItem.model_validate(a) for a in articles]
    page_data = PageResult.create(items=items, total=total, page=page, size=size)
    return Result.success(data=page_data)


@router.get("/{id_or_slug}", response_model=Result[ArticleDetail], summary="根据ID或别名获取文章详情")
def get_article_detail(
    id_or_slug: str,
    db: Session = Depends(get_db)
):
    query = db.query(Article).options(
        joinedload(Article.category),
        joinedload(Article.tags),
        joinedload(Article.author)
    )
    if id_or_slug.isdigit():
        article = query.filter(Article.id == int(id_or_slug)).first()
    else:
        article = query.filter(Article.slug == id_or_slug).first()

    if not article:
        raise BusinessException("博文不存在或已删除", code=404)

    # 浏览量自增
    article.views_count += 1
    db.commit()
    db.refresh(article)

    return Result.success(data=ArticleDetail.model_validate(article))


@router.post("", response_model=Result[ArticleDetail], summary="创建文章并自动同步构建 RAG 向量切片 (管理员)")
def create_article(
    payload: ArticleCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    exist = db.query(Article).filter(Article.slug == payload.slug).first()
    if exist:
        raise BusinessException("文章别名 slug 已存在，请换一个唯一英文或拼音标识", code=400)

    article_data = payload.model_dump(exclude={"tag_ids"})
    article = Article(**article_data, author_id=admin.id)

    # 关联标签
    if payload.tag_ids:
        tags = db.query(Tag).filter(Tag.id.in_(payload.tag_ids)).all()
        article.tags = tags

    db.add(article)
    db.commit()
    db.refresh(article)

    # 核心步骤：触发自动化文本分块与特征向量化写入 RAG 知识库
    try:
        rag_service.index_article(db, article.id)
    except Exception as e:
        article.vector_status = "failed"
        db.commit()

    db.refresh(article)
    return Result.success(data=ArticleDetail.model_validate(article), message="文章发布并成功录入 AI 知识库")


@router.put("/{id}", response_model=Result[ArticleDetail], summary="更新文章与重新同步向量索引 (管理员)")
def update_article(
    id: int,
    payload: ArticleUpdate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin)
):
    article = db.query(Article).filter(Article.id == id).first()
    if not article:
        raise BusinessException("文章不存在", code=404)

    update_dict = payload.model_dump(exclude_unset=True)
    tag_ids = update_dict.pop("tag_ids", None)

    for field, val in update_dict.items():
        setattr(article, field, val)

    if tag_ids is not None:
        tags = db.query(Tag).filter(Tag.id.in_(tag_ids)).all()
        article.tags = tags

    db.commit()
    db.refresh(article)

    # 重构向量切片
    try:
        rag_service.index_article(db, article.id)
    except Exception:
        article.vector_status = "failed"
        db.commit()

    db.refresh(article)
    return Result.success(data=ArticleDetail.model_validate(article), message="文章更新并重新建立向量索引")


@router.delete("/{id}", response_model=Result[None], summary="删除文章 (管理员)")
def delete_article(
    id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin)
):
    article = db.query(Article).filter(Article.id == id).first()
    if not article:
        raise BusinessException("文章不存在", code=404)

    db.delete(article)
    db.commit()
    return Result.success(message="文章及关联向量切片已彻底删除")


@router.post("/{id}/like", response_model=Result[int], summary="文章点赞")
def like_article(id: int, db: Session = Depends(get_db)):
    article = db.query(Article).filter(Article.id == id).first()
    if not article:
        raise BusinessException("文章不存在", code=404)

    article.likes_count += 1
    db.commit()
    return Result.success(data=article.likes_count, message="点赞成功")


@router.post("/{id}/reindex", response_model=Result[int], summary="手动触发该文章向量索引重构 (管理员)")
def reindex_article(
    id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin)
):
    chunks_count = rag_service.index_article(db, id)
    return Result.success(data=chunks_count, message=f"已成功切分并建立 {chunks_count} 个向量知识切片")
