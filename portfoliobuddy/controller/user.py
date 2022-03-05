from portfoliobuddy.model import session, User


def user_exists(user_id):
    db_session = session()
    result = db_session.query(User).filter(User.userid.is_(user_id))
    return bool(result.all())


def get_chat_id():
    db_session = session()
    result = db_session.query(User).filter(User.username.like('Group Chat'))
    row = result.first()
    if row:
        return row.userid
