i18n = import('i18n')
message('Update translations')

r = run_command('cat', 'LINGUAS')
if r.returncode() != 0
    error('Cannot find po/LINGUAS')
endif

langs = r.stdout().strip().split()
i18n.gettext('Authenticator', languages : langs)
