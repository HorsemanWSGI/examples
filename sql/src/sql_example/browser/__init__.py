import pathlib
from typing import Any

import horseman.response
from horseman.meta import APIView
from chameleon.zpt.loader import TemplateLoader


TEMPLATES = TemplateLoader(
    str(pathlib.Path(__file__).parent / 'templates')
)


class Form(APIView):
    model: Any
    form: Any

    template = TEMPLATES['form.pt']
    layout = TEMPLATES['layout.pt']


class AddForm(Form):

    def POST(self, request):
        data = request.extract()
        form = self.form(data.form)
        if form.validate():
            obj = self.model()
            form.populate_obj(obj)
            request.sql_session.add(obj)
            return horseman.response.redirect('/')
        html = self.template.render(
            title='New',
            action=request.route.path,
            form=form,
            layout=self.layout,
        )
        return horseman.response.reply(
            200, body=html,
            headers={"Content-Type": "text/html; charset=utf-8"}
        )

    def GET(self, request):
        html = self.template.render(
            title='New',
            action=request.route.path,
            form=self.form(),
            layout=self.layout,
        )
        return horseman.response.reply(
            200, body=html,
            headers={"Content-Type": "text/html; charset=utf-8"}
        )


class EditForm(Form):

    def get_context(self, request):
        raise NotImplementedError('Implemented your own.')

    def POST(self, request, **kwargs):
        data = request.extract()
        context = self.get_context(request)
        form = self.form(data.form, obj=context)
        if form.validate():
            form.populate_obj(context)
            return horseman.response.redirect('/')
        html = self.template.render(
            title='Edit',
            action=request.route.path,
            form=form,
            layout=self.layout,
        )
        return horseman.response.reply(
            200, body=html,
            headers={"Content-Type": "text/html; charset=utf-8"}
        )

    def GET(self, request, **kwargs):
        context = self.get_context(request)
        form = self.form(obj=context)
        html = self.template.render(
            title='Edit',
            action=request.route.path,
            form=form,
            layout=self.layout,
        )
        return horseman.response.reply(
            200, body=html,
            headers={"Content-Type": "text/html; charset=utf-8"}
        )
