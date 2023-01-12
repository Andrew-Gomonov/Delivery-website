from App import conn, cur


class News:
    def __init__(self, news_id: int):
        cur.execute(f"select id from News where id='{news_id}'")
        info = cur.fetchone()
        if info is None:
            raise ValueError("News not found in database")
        self.news_id = news_id

    def get(self):
        """
        Get news by id
        :return: dictionary that contain id,title,content,publish_date,image
        """
        json_data = {}
        cur.execute(f"select * from News where id='{self.news_id}'")
        news = cur.fetchone()
        json_data.update({
            "id": news[0],
            "title": news[1],
            "content": news[2],
            "image": news[3],
            "author": news[4],
            "datetime": str(news[5])
        })
        return json_data

    def delete(self) -> dict[str, str | int]:
        """
        Delete news by id
        :return: code and message
        """
        cur.execute(f"DELETE FROM News WHERE id='{self.news_id}'")
        conn.commit()
        return {"Code": 200, "msg": "News deleted successfully"}

    def edit(self, data_to_edit: dict) -> dict[str, str | int]:
        """
        Edit news by dictionary
        :param data_to_edit: this is a dictionary in which there should be data to change
        :return: code and message
        """
        result = ""
        for key, value in data_to_edit.items():
            result += f"{key} = '{value}',"
        result = result[:-1]
        cur.execute(f"UPDATE News SET {result} WHERE id='{self.news_id}'")
        return {"Code": 200, "msg": "News updated successfully"}


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


def create_news(data_news: dict) -> dict[str, str | int]:
    """
    Create news by a dictionary
    :param data_news: this is a dictionary that should contain the keys title, content, image, author
    :return: code and message
    """
    for key in data_news.keys():
        if key not in ['title', 'content', 'image', 'author']:
            raise KeyError("Unknown field in news dictionary")
    cur.execute(
        "INSERT INTO News (title, content, publish_date,image_url,author)"
        " VALUES ('{0}', '{1}', CURRENT_TIMESTAMP,'{2}','{3}');"
        .format(data_news['title'], data_news['content'], data_news['image'], data_news['author'])
    )
    conn.commit()
    return {"Code": 201, "msg": "News created"}


def search_news(data_to_search: dict):
    for key in data_to_search.keys():
        if key not in ['title', 'content', 'image']:
            raise KeyError("Unknown field in url")
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
        return {"Code": 404, "msg": "News not found in database"}
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
