from django import forms

from apps.common.models import DepartmentLevelSubject

from apps.courses.models import DepartmentLevel


class DepartmentLevelChoiceForm(forms.Form):
    department_levels = forms.ModelMultipleChoiceField(
        queryset=DepartmentLevel.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        label="Sélectionnez les filières",
        required=True,
    )

    def __init__(self, *args, **kwargs):
        allowed_department_levels = kwargs.pop("allowed_department_levels", None)
        super().__init__(*args, **kwargs)
        if allowed_department_levels is not None:
            self.fields["department_levels"].queryset = DepartmentLevel.objects.filter(
                id__in=[dl.id for dl in allowed_department_levels]
            )
