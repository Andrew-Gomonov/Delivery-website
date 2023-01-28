from App import conn, cur
from App.errors.api import APIBadRequestError


def get_news() -> list[dict[str, str]]:
    """
    Get all news in database
    :return: returns a list of dictionaries that contain
    id,title,text,datetime,image,author
    """
    news_list = []
    cur.execute("SELECT * from News")
    news_info = cur.fetchall()
    for news in news_info:
        news_list.append({
            "id": news[0],
            "title": news[1],
            "content": news[2],
            "image": news[3],
            "author": news[4],
            "datetime": str(news[5])
        })
    return news_list


def create_news(data_news: dict) -> bool:
    """
    Create news by a dictionary
    :param data_news: this is a dictionary that should contain the keys title, content, image, author
    :return: code and message
    """
    for key in data_news.keys():
        if key not in ['title', 'content', 'image', 'author']:
            raise APIBadRequestError("Unknown field in news dictionary")
    cur.execute(
        "INSERT INTO News (title, content, publish_date,image_url,author)"
        " VALUES ('{0}', '{1}', CURRENT_TIMESTAMP,'{2}','{3}');"
        .format(data_news['title'], data_news['content'], data_news['image'], data_news['author'])
    )
    conn.commit()
    return True
