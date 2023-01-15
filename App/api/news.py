from App import conn, cur
from App.errors.api import APINotFoundError, APIBadRequestError


class News:
    def __init__(self, news_id: int):
        cur.execute(f"select * from News where id='{news_id}'")
        info = cur.fetchone()
        if info is None:
            raise APINotFoundError("News not found in database")
        self.id: int = news_id
        self.title: str = info[1]
        self.content: str = info[2]
        self.image: str = info[3]
        self.author: str = info[4]
        self.datetime = str(info[5])

    def to_dict(self):
        """
        Get news in dict
        :return: dictionary that contain id,title,content,publish_date,image
        """
        json_data = {}
        json_data.update({
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "image": self.image,
            "author": self.author,
            "datetime": self.datetime
        })
        return json_data

    def delete(self) -> bool:
        """
        Delete news by id
        :return: code and message
        """
        cur.execute(f"DELETE FROM News WHERE id='{self.id}'")
        conn.commit()
        return True

    def edit(self, data_to_edit: dict) -> bool:
        """
        Edit news by dictionary
        :param data_to_edit: this is a dictionary in which there should be data to change
        :return: code and message
        """
        result = ""
        for key, value in data_to_edit.items():
            result += f"{key} = '{value}',"
        result = result[:-1]
        cur.execute(f"UPDATE News SET {result} WHERE id='{self.id}'")
        return True


def get_news() -> list[dict[str, str]]:
    """
    Get all news in database
    :return: returns a list of dictionaries that contain
    id,title,text,datetime,image,author
    """
    json_data = []
    cur.execute("SELECT * from News")
    news_array = cur.fetchall()
    for news in news_array:
        json_data.append({
            "id": news[0],
            "title": news[1],
            "content": news[2],
            "image": news[3],
            "author": news[4],
            "datetime": str(news[5])
        })
    return json_data


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


def search_news(data_to_search: dict):
    for key in data_to_search.keys():
        if key not in ['title', 'content', 'image']:
            raise APIBadRequestError("Unknown field in url")
    result = ""
    for key, value in data_to_search.items():
        if not value.isnumeric():
            result += f"{key} LIKE('%{value}%') AND "
        else:
            result += f"{key} = '{value}' AND "
    result = result[:-5]
    json_data = []
    cur.execute(f"SELECT * from News WHERE {result};")
    news_array = cur.fetchall()
    if len(news_array) == 0:
        raise APINotFoundError("News not found in database")
    for news in news_array:
        json_data.append({
            "id": news[0],
            "title": news[1],
            "content": news[2],
            "image": news[3],
            "author": news[4],
            "datetime": str(news[5])
        })
    return json_data
