from django import template

register = template.Library()


@register.filter
def get_filiere_name(student):
    """
    Retourne le nom de la filière depuis l'objet student.
    """
    if hasattr(student, "major") and student.major:
        if hasattr(student.major, "departmentlevel"):
            return f"{student.major.departmentlevel.department.name} - {student.major.departmentlevel.level.name}"
        elif hasattr(student.major, "department"):
            return student.major.department.name
    return "Non assigné"
