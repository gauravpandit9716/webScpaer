-- CREATE DATABASE IF NOT EXISTS scraper; 

-- USE scraper;
---------------------------------table scrape_status -----------------------------------------------------

-- __tablename__ = "scrape_status"
    
--     id = Column(Integer, primary_key=True, index=True)
--     status = Column(String(50), index=True)
--     created_at = Column(DateTime, default=func.now(), index=True)

-- create table if not exists scrape_status(
--   id int(10) unsigned primary key not null auto_increment,
--   status varchar(50),
--   created_at timestamp default current_timestamp
-- );

--  select * from scraper.scrape_status

-----------------------------------------table posts------------------------------------------------
-- __tablename__ = "posts"

--     id = Column(Integer, primary_key=True, index=True)
--     title = Column(String(256))
--     points = Column(Integer)
--     author = Column(String(50))
--     posted_time = Column(String(50))
--     created_at = Column(DateTime, default=func.now())

-- create table posts(
--     id int(10) unsigned primary key not null auto_increment,
--     title varchar(256),
--     points int(10),
--     author varchar(100),
--     posted_time varchar(100),
--     created_at timestamp,
--      comments varchar(10000)
-- )

-- select * from scraper.posts
--------------------------------------table comments--------------------------------------------------

--   __tablename__ = "comments"

--     id = Column(Integer, primary_key=True, index=True)
--     post_id = Column(Integer, ForeignKey("posts.id"))
--     text = Column(String(1024))
--     post = relationship("Post", back_populates="comments")

-- create table comments(
--     id int(10) unsigned primary key not null auto_increment,
--     post_id int(10) unsigned not null,
--     CONSTRAINT fk_posts FOREIGN KEY (post_id)  
--     REFERENCES posts(id)  
--       ON DELETE CASCADE  
--       ON UPDATE CASCADE ,
--     text varchar(10000),
--     post varchar(100)
-- )