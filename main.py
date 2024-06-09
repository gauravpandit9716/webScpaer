import uvicorn
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import  Session
from scraper import scrape_and_save_data
from model import ScrapeStatus,Post, StatusResponse,get_db,save_status,Comment

###########----API Endpoints Creation----------------------------------------

app = FastAPI()

@app.get("/test",response_model={})
async def test():
    data = {"status" : "welcome to web scraper application"}
    return data

@app.post("/scrape", status_code=201)
async def scrape_data(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    db_status = save_status(db, "in_progress")
    background_tasks.add_task(scrape_and_save_data, db_status.id)
    return {"message": "Scraping started"}

@app.get("/data", response_model={})
async def get_data(db: Session = Depends(get_db)):
    posts = db.query(Post).all()
    comments = db.query(Comment).all()
    data = {"posts":posts,'comments': comments}
    return data

@app.get("/status", response_model=StatusResponse)
async def get_status(db: Session = Depends(get_db)):
    status = db.query(ScrapeStatus).order_by(ScrapeStatus.created_at.desc()).first()
    if not status:
        raise HTTPException(status_code=404, detail="No status found")
    return status

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
