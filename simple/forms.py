from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions
from django import forms
from django.core.urlresolvers import reverse

class BlogForm(forms.Form):
    title = forms.CharField(max_length=100)
    summary = forms.CharField(widget=forms.Textarea, required=False)
    body = forms.CharField(widget=forms.Textarea)
    is_markdown = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        forms.Form.__init__(self, *args, **kwargs)
        legend = "Edit Blog Post"
        submit_value = 'Save'
        ajax_form = 'list-None-form'
        submit_id = 'action-button'
        cancel_id = 'cancel-button'
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('title', css_class='input-xlarge'),
            Field('is_markdown', css_class='input-xlarge'),
            Field('summary', css_class='field span12'),
            Field('body', css_class='field span12'),
            )
        self.helper.layout.insert(0, HTML('<legend>%s</legend>' % legend))
        self.helper.layout.append(
            FormActions(
                Submit('action', submit_value, css_class="btn-primary", ajax_form=ajax_form, id=submit_id),
                Submit('action', 'Cancel', id=cancel_id),
                )
            )

class CommentForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': '@me'}), required=False)
    pingback = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'http://wwww.'}), required=False)
    comment = forms.CharField(widget=forms.Textarea)

    def __init__(self, reference_type=None, reference_to=None, *args, **kwargs):
        forms.Form.__init__(self, *args, **kwargs)
        legend = 'New Comment'
        submit_value = 'Create'
        ajax_form = 'list-None-form'
        submit_id = 'action-button'
        cancel_id = 'cancel-button'
        self.reference_to = reference_to
        self.reference_type = reference_type
        self.helper = FormHelper()
        self.helper.form_action = reverse('comment_create', args=(reference_type, reference_to))
        self.helper.layout = Layout(
            Field('name', css_class='field span12'),
            Field('pingback', css_class="field span12"),
            Field('comment', css_class="field span12"),
            )
        self.helper.layout.insert(0, HTML('<legend>%s</legend>' % legend))
        self.helper.layout.append(
            FormActions(
                Submit('action', submit_value, css_class="btn-primary", ajax_form=ajax_form, id=submit_id),
                Submit('action', 'Cancel', id=cancel_id),
                )
            )




