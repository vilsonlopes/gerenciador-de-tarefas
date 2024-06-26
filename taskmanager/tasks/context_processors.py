
def feature_flags(request):
    user = request.user
    flags = {
        'is_priority_feature_enabled': False,
    }
    # Certifique-se de que o usuário esteja autenticado antes de verificar os grupos
    if user.is_authenticated:
        flags['is_priority_feature_enabled'] = user.groups.filter(
            name='Task Prioritization Beta Testers'
        ).exists()
    return flags
