from django import forms

from .models import Rsvp


class RsvpForm(forms.ModelForm):
    class Meta:
        model = Rsvp
        fields = ('name', 'attendance', 'with_children', 'phone', 'wish')
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Имя Фамилия', 'autocomplete': 'name'}),
            'attendance': forms.RadioSelect(),
            'with_children': forms.CheckboxInput(),
            'phone': forms.TextInput(
                attrs={'placeholder': '+7 (___) ___ __ __', 'inputmode': 'tel', 'autocomplete': 'tel'}
            ),
            'wish': forms.Textarea(attrs={'placeholder': 'Пожелание молодожёнам (по желанию)', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # у CharField с choices Django добавляет пустой вариант «---------»
        self.fields['attendance'].choices = Rsvp.ATTENDANCE_CHOICES
        self.fields['phone'].required = False
        self.fields['wish'].required = False

    def clean_with_children(self):
        return self.cleaned_data['with_children'] and self.cleaned_data.get('attendance') == Rsvp.COUPLE

    def clean_name(self):
        name = self.cleaned_data['name'].strip()
        if len(name) < 2:
            raise forms.ValidationError('Пожалуйста, укажите имя и фамилию')
        return name
