from django import forms
from django.contrib.auth.models import User
from .models import UserProfile

# Define choices for Program, Department, and Year
PROGRAM_CHOICES = [
    ('BSA-AGRI', 'Bachelor of Science in Agriculture'),
    ('BSP-PHARM', 'Bachelor of Science in Pharmacy'),
    ('BSB', 'Bachelor of Science in Biology'),
    ('BSRT', 'Bachelor of Science in Radiologic Technology'),
    ('BSMT', 'BS in Medical Technology/ Medical Laboratory Science'),
    ('BSP-PSY', 'Bachelor of Science in Psychology'),
    ('BSSW', 'Bachelor of Science in Social Work'),
    ('BSA-ACC', 'Bachelor of Science in Accountancy'),
    ('BSMA', 'Bachelor of Science in Management Accounting'),
    ('BSBA', 'Bachelor of Science in Business Administration'),
    ('BSE', 'Bachelor of Science in Entrepreneurship'),
    ('BSTM', 'Bachelor of Science in Tourism Management'),
    ('BSC', 'Bachelor of Science in Criminology'),
    ('BSCE', 'Bachelor of Science in Civil Engineering'),
    ('BSIT', 'Bachelor of Science in Information Technology'),
    ('BSEMC', 'BS in Entertainment and Multimedia Computing'),
    ('BSN', 'Bachelor of Science in Nursing'),
    ('BECE', 'Bachelor of Early Childhood Education'),
    ('BEE', 'Bachelor of Elementary Education'),
    ('BSE-EDU', 'Bachelor of Secondary Education'),
    ('BTVTE', 'Bachelor of Technical - Vocational Teacher Education'),
]


DEPARTMENT_CHOICES = [
    ('CA', 'College of Agriculture'),
    ('CAHSE', 'College of Allied Health Science Education'),
    ('CAS', 'College of Arts and Sciences'),
    ('CBE', 'College of Business Education'),
    ('CCJE', 'College of Criminal Justice Education'),
    ('CE', 'College of of Engineering'),
    ('CITE', 'College of Information Technology'),
    ('CN', 'College of Nursing'),
    ('CTE', 'College of Teacher Education'),
]

YEAR_CHOICES = [
    ('1', '1st Year'),
    ('2', '2nd Year'),
    ('3', '3rd Year'),
    ('4', '4th Year'),
    ('5', '5th Year'),
]

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    gender = forms.ChoiceField(choices=UserProfile.GENDER_CHOICES)
    program = forms.ChoiceField(choices=PROGRAM_CHOICES)
    department = forms.ChoiceField(choices=DEPARTMENT_CHOICES)
    year = forms.ChoiceField(choices=YEAR_CHOICES)
    student_id = forms.CharField(max_length=20)


    class Meta:
        model = User
        fields = [
            'username', 'student_id', 'email', 'first_name', 'last_name',
            'password', 'confirm_password',
            'gender',  'program', 'department', 'year'
        ]


    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email.endswith('@jmc.edu.ph'):
            raise forms.ValidationError("Only emails under @jmc.edu.ph are allowed.")
        return email


class EditProfileForm(forms.ModelForm):
    student_id = forms.CharField(
    max_length=20,
    widget=forms.TextInput(attrs={'class': 'form-control'}),
    label="Student ID"
    )
     
    gender = forms.ChoiceField(
        choices=UserProfile.GENDER_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Gender"
    )

    program = forms.ChoiceField(
        choices=PROGRAM_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Program"
    )
    department = forms.ChoiceField(
        choices=DEPARTMENT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Department"
    )
    year = forms.ChoiceField(
        choices=YEAR_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Year Level"
    )

    class Meta:
        model = User
        fields = ['student_id', 'first_name', 'last_name', 'email', 'gender', 'program', 'department', 'year']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(EditProfileForm, self).__init__(*args, **kwargs)

        if hasattr(user, 'userprofile'):
            self.fields['gender'].initial = user.userprofile.gender
            self.fields['student_id'].initial = user.userprofile.student_id
            self.fields['program'].initial = user.userprofile.program
            self.fields['department'].initial = user.userprofile.department
            self.fields['year'].initial = user.userprofile.year
