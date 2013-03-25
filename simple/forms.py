from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions
from django import forms
from django.core.urlresolvers import reverse

class BlogForm(forms.Form):
    title = forms.CharField(max_length=100)
    body = forms.CharField()

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
    pingback = forms.CharField()
    comment = forms.CharField()

#    class Meta:
#        model = Comment
#        fields = ['pingback', 'comment']
#        exclude = ['reference', 'is_spam']
#        widgets = {'comment': forms.Textarea(attrs=dict(rows=4))}

    def __init__(self, reference_type=None, reference_to=None, *args, **kwargs):
        forms.Form.__init__(self, *args, **kwargs)
        legend = 'New Comment'
        submit_value = 'Create'
        ajax_form = 'list-None-form'
        submit_id = 'action-button'
        cancel_id = 'cancel-button'
        self.helper = FormHelper()
        self.helper.form_action = reverse('comment_create', args=(reference_type, reference_to))
        self.helper.layout = Layout(
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




