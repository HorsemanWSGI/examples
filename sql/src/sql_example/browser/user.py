import horseman.response
from wtforms_sqlalchemy.orm import model_form

from sql_example.app import routes
from sql_example.browser import AddForm, EditForm, TEMPLATES
from sql_example.models import User
from sql_example.request import Request


@routes.register('/')
def index(request: Request):
    users = request.sql_session.query(User).all()
    template = TEMPLATES['listing.pt']
    layout = TEMPLATES['layout.pt']
    html = template.render(
        users=users,
        layout=layout
    )
    return horseman.response.reply(
        200, body=html,
        headers={"Content-Type": "text/html; charset=utf-8"}
    )


@routes.register('/new', )
class AddUser(AddForm):

    model = User
    form = model_form(User, exclude_pk=True)


@routes.register('/{uid:digit}/edit')
class EditUser(EditForm):

    model = User
    form = model_form(User, exclude_pk=True)

    def get_context(self, request):
        return request.sql_session.query(
            self.model).get(request.route.params['uid'])


@routes.register('/{uid:digit}/delete')
def delete(request: Request, uid: int):
    user = request.sql_session.query(User).get(uid)
    request.sql_session.delete(user)
    return horseman.response.redirect('/')
