import pathlib
from typing import Any, ClassVar

import horseman.response
from horseman.meta import APIView
from chameleon.zpt.loader import TemplateLoader
from sql_example import models
from wtforms_sqlalchemy.orm import model_form


TEMPLATES = TemplateLoader(
    str(pathlib.Path(__file__).parent / 'templates')
)


class Form(APIView):

    modelname: ClassVar[str]

    template = TEMPLATES['form.pt']
    layout = TEMPLATES['layout.pt']

    @property
    def model(self):
        return models.registry[self.modelname]

    @property
    def form(self):
        return model_form(self.model, exclude_pk=True)

    def render(self, **namespace):
        html = self.template.render(layout=self.layout, **namespace)
        return horseman.response.Response.html(body=html)


class AddForm(Form):

    def POST(self, request):
        data = request.extract()
        form = self.form(data.form)
        if form.validate():
            obj = self.model()
            form.populate_obj(obj)
            request.sql_session.add(obj)
            return horseman.response.Response.redirect('/')
        return self.render(
            title='New', form=form, action=request.route.path)

    def GET(self, request):
        return self.render(
            title='New', form=self.form(), action=request.route.path)


class EditForm(Form):

    def get_context(self, request):
        raise NotImplementedError('Implemented your own.')

    def POST(self, request, **kwargs):
        data = request.extract()
        context = self.get_context(request)
        form = self.form(data.form, obj=context)
        if form.validate():
            form.populate_obj(context)
            return horseman.response.Response.redirect('/')
        return self.render(
            title='Edit', form=form, action=request.route.path)

    def GET(self, request, **kwargs):
        context = self.get_context(request)
        form = self.form(obj=context)
        return self.render(
            title='Edit', form=form, action=request.route.path)
