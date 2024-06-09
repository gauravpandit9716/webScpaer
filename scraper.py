from fastapi import HTTPException
import requests
from bs4 import BeautifulSoup
from model import PostCreate
from datetime import datetime
from model import ScrapeStatus,Post,update_status,Comment,SessionLocal


def scrape_latest_posts():
    url = "https://news.ycombinator.com/news"
    print(f"Fetching posts from: {url}")
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching the URL: {str(e)}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    print("Parsed HTML content")

    posts = soup.select('.athing')[:30]
    print(f"Found {len(posts)} posts")

    posts_data = []

    for index, post in enumerate(posts):
        title_tag = post.select_one('.titleline > a')
        if title_tag:
            title = title_tag.get_text()
        else:
            print(f"No title found for post {index+1}")
            continue

        subtext = post.find_next_sibling('tr').select_one('.subtext')
        if not subtext:
            print(f"No subtext found for post {index+1}")
            continue

        points_tag = subtext.select_one('.score')
        points = int(points_tag.get_text().split()[0]) if points_tag else 0

        author_tag = subtext.select_one('.hnuser')
        author = author_tag.get_text() if author_tag else 'Unknown'

        posted_time_tag = subtext.select_one('.age a')
        posted_time = posted_time_tag.get_text() if posted_time_tag else 'Unknown'

        post_url = title_tag['href'] if title_tag else '#'
        if not post_url.startswith('http'):
            post_url = f'https://news.ycombinator.com/{post_url}'

        print(f"Post {index+1}: Title: {title}, Points: {points}, Author: {author}, Posted Time: {posted_time}, Post URL: {post_url}")

        try:
            comments = scrape_latest_comments(post_url)
        except HTTPException as e:
            print(f"Skipping comments for post {index+1} due to error: {e.detail}")
            comments = []

        posts_data.append(PostCreate(
            title=title,
            points=points,
            author=author,
            posted_time=posted_time,
            comments=comments
        ))

    return posts_data


def scrape_latest_comments(post_url: str):
    print(f"Fetching comments from: {post_url}")
    if not post_url.startswith('http'):
        post_url = f'https://news.ycombinator.com/{post_url}'

    try:
        response = requests.get(post_url)
        response.raise_for_status()
    except requests.RequestException as e:
        if response.status_code == 403:
            print(f"Forbidden URL: {post_url}")
        else:
            print(f"Error fetching the post URL: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

    soup = BeautifulSoup(response.content, 'html.parser')
    print("Parsed HTML content for comments")

    comment_items = soup.select('.comment')
    print(f"Found {len(comment_items)} comments")

    comments_data = [comment.get_text().strip() for comment in comment_items if comment.get_text().strip()]

    if len(comments_data) < 5:
        print(f"Only {len(comments_data)} comments found for post, returning available comments")
    else:
        comments_data = comments_data[:5]

    print(f"Comments: {comments_data}")

    return comments_data


def scrape_and_save_data(status_id: int):
    db = SessionLocal()
    try:
        db_status = db.query(ScrapeStatus).filter(ScrapeStatus.id == status_id).one()
        posts_data = scrape_latest_posts()
        for post_data in posts_data:
            post = Post(
                title=post_data.title,
                points=post_data.points,
                author=post_data.author,
                posted_time=post_data.posted_time,
                created_at=datetime.utcnow()
            )
            db.add(post)
            db.commit()
            db.refresh(post)
            for comment in post_data.comments:
                db_comment = Comment(
                    post_id=post.id,
                    text=comment[0]
                )
                db.add(db_comment)
                db.commit()
                db.refresh(db_comment)
        update_status(db, db_status, "completed")
    except Exception as e:
        print(f"Scraping failed: {str(e)}")
        db_status = db.query(ScrapeStatus).filter(ScrapeStatus.id == status_id).one()
        update_status(db, db_status, "failed")