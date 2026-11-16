# ==============================================================================
# MINECRAFT CTF - ACTIVE DIRECTORY SIMULADO PARA THE END (PowerView)
# Desarrollado por: Thorfinn777, Martyn777, Sassyjack777
#
# Esta consola NO ejecuta PowerShell, PowerView ni comandos del sistema.
# Solo resuelve los comandos permitidos contra un dominio de Active Directory
# ficticio (end.local) definido en este mismo archivo.
# ==============================================================================

import shlex
import textwrap

MAX_COMMAND_LENGTH = 300
EGG_FLAG_PLACEHOLDER = '@@EGG_FLAG@@'

DOMAIN = 'end.local'
DOMAIN_NETBIOS = 'END'
DOMAIN_SID = 'S-1-5-21-3117384521-1935557925-2848026150'
DC_NAME = 'END-DC01'
FS_NAME = 'END-FS01'

FS_UNC = r'\\END-FS01'
PUBLIC_UNC = FS_UNC + r'\public'
VAULT_UNC = FS_UNC + r'\vault'
EGG_UNC = VAULT_UNC + r'\real_dragon_egg.txt'
PUBLIC_README_UNC = PUBLIC_UNC + r'\readme.txt'

# ------------------------------------------------------------------------------
# USUARIOS DEL DOMINIO
# ------------------------------------------------------------------------------
USERS = {
    'steve': {
        'name': 'Steve',
        'description': 'Explorador del Overworld. Cuenta de usuario estándar.',
        'enabled': 'True',
        'groups': ['Domain Users'],
        'lastlogon': '2026-11-14 21:42',
    },
    'alex': {
        'name': 'Alex',
        'description': 'Constructora del End City y de las torres de cristal.',
        'enabled': 'True',
        'groups': ['Domain Users', 'End Builders'],
        'lastlogon': '2026-11-15 09:18',
    },
    'svc_backup': {
        'name': 'svc_backup',
        'description': r'Cuenta de servicio de copias del altar. El vault del Huevo se publica en \\END-FS01\vault.',
        'enabled': 'True',
        'groups': ['Domain Users', 'End Vault Admins'],
        'lastlogon': '2026-11-14 21:05',
    },
    'svc_telemetry': {
        'name': 'svc_telemetry',
        'description': 'Servicio de telemetría de los cristales del End.',
        'enabled': 'True',
        'groups': ['Domain Users', 'Server Operators'],
        'lastlogon': '2026-11-16 07:55',
    },
    'ender_admin': {
        'name': 'ender_admin',
        'description': 'Administrador del dominio end.local.',
        'enabled': 'True',
        'groups': ['Domain Admins', 'Domain Users', 'End Vault Admins'],
        'lastlogon': '2026-11-12 18:30',
    },
}

# ------------------------------------------------------------------------------
# GRUPOS DEL DOMINIO
# ------------------------------------------------------------------------------
GROUPS = {
    'Domain Users': {
        'description': 'Todos los usuarios del dominio.',
        'members': ['steve', 'alex', 'svc_backup', 'svc_telemetry', 'ender_admin'],
    },
    'Domain Admins': {
        'description': 'Administradores del dominio.',
        'members': ['ender_admin'],
    },
    'End Vault Admins': {
        'description': 'Acceso al recurso compartido del vault del Huevo de Dragón.',
        'members': ['svc_backup', 'ender_admin'],
    },
    'Server Operators': {
        'description': 'Operadores de los servidores del End.',
        'members': ['svc_telemetry'],
    },
    'End Builders': {
        'description': 'Constructores de estructuras del End City.',
        'members': ['alex'],
    },
}

# ------------------------------------------------------------------------------
# EQUIPOS DEL DOMINIO
# ------------------------------------------------------------------------------
COMPUTERS = {
    'END-DC01': {
        'fqdn': 'END-DC01.end.local',
        'os': 'Windows Server 2022 Standard',
        'description': 'Controlador de dominio de end.local.',
        'ip': '10.13.37.10',
    },
    'END-FS01': {
        'fqdn': 'END-FS01.end.local',
        'os': 'Windows Server 2019 Standard',
        'description': 'Servidor de archivos y vault del Huevo de Dragón.',
        'ip': '10.13.37.20',
    },
    'END-WS01': {
        'fqdn': 'END-WS01.end.local',
        'os': 'Windows 10 Pro',
        'description': 'Estación de trabajo de Steve.',
        'ip': '10.13.37.31',
    },
}

# ------------------------------------------------------------------------------
# RECURSOS COMPARTIDOS (SMB)
# ------------------------------------------------------------------------------
SHARES = {
    'END-DC01': [
        {
            'name': 'NETLOGON',
            'path': r'\\END-DC01\NETLOGON',
            'description': 'Scripts de inicio de sesión del dominio.',
            'admin': True,
        },
        {
            'name': 'SYSVOL',
            'path': r'\\END-DC01\SYSVOL',
            'description': 'Directorio compartido del sistema del dominio.',
            'admin': True,
        },
    ],
    'END-FS01': [
        {
            'name': 'public',
            'path': PUBLIC_UNC,
            'description': 'Documentación pública del altar del End.',
            'admin': False,
        },
        {
            'name': 'vault',
            'path': VAULT_UNC,
            'description': 'Almacén del Huevo de Dragón (acceso restringido a End Vault Admins).',
            'admin': False,
        },
        {
            'name': 'IPC$',
            'path': r'\\END-FS01\IPC$',
            'description': 'Remote IPC.',
            'admin': True,
        },
    ],
    'END-WS01': [
        {
            'name': 'Users',
            'path': r'\\END-WS01\Users',
            'description': 'Perfiles de usuario locales.',
            'admin': True,
        },
    ],
}

# Sesiones visibles para Invoke-UserHunter
SESSIONS = [
    {
        'user': 'svc_backup',
        'domain': DOMAIN_NETBIOS,
        'computer': 'END-FS01',
        'ip': '10.13.37.20',
        'session_time': '2026-11-14 21:05',
    },
    {
        'user': 'steve',
        'domain': DOMAIN_NETBIOS,
        'computer': 'END-WS01',
        'ip': '10.13.37.31',
        'session_time': '2026-11-16 08:12',
    },
]

# Archivos virtuales de los recursos compartidos públicos.
PUBLIC_FILES = {
    # Se guarda ya normalizada (sin barras iniciales) para comparar con
    # _normalize_unc, que también elimina las barras invertidas iniciales.
    PUBLIC_README_UNC.replace('/', '\\').lstrip('\\').lower(): textwrap.dedent("""
        ALTAR DEL END - DOCUMENTACIÓN PÚBLICA
        -------------------------------------
        Las copias del altar se guardan en el servidor de archivos END-FS01.

        Recurso compartido del vault:
          \\\\END-FS01\\vault

        El trofeo del dragón se archiva como real_dragon_egg.txt.
        Solo el grupo "End Vault Admins" tiene acceso al vault.
    """).strip('\n') + '\n',
}

EGG_FILE = EGG_FLAG_PLACEHOLDER + '\n'


def _result(output, kind='text', ok=True):
    return {'ok': ok, 'kind': kind, 'output': output}


def _error(message):
    return {'ok': False, 'kind': 'error', 'output': message}


def _clean(token):
    """Quita las comillas que shlex(posix=False) conserva en los argumentos."""
    return (token or '').strip().strip('"').strip("'")


def _normalize_unc(path):
    """Normaliza una ruta UNC para compararla sin distinguir mayúsculas."""
    value = _clean(path).replace('/', '\\')
    value = value.lstrip('\\')
    while '\\\\' in value:
        value = value.replace('\\\\', '\\')
    return value.lower()


def _parse_arguments(args):
    """Separa opciones (-Nombre valor) de los argumentos posicionales."""
    positional = []
    options = {}
    index = 0

    while index < len(args):
        token = _clean(args[index])
        if token.startswith('-') and len(token) > 1:
            key = token.lstrip('-').lower()
            if '=' in key:
                key, inline_value = key.split('=', 1)
                options[key] = _clean(inline_value)
            elif index + 1 < len(args) and not _clean(args[index + 1]).startswith('-'):
                options[key] = _clean(args[index + 1])
                index += 1
            else:
                options[key] = ''
        else:
            positional.append(token)
        index += 1

    return positional, options


def _first_option(options, *names):
    for name in names:
        value = options.get(name)
        if value:
            return value
    return ''


def _find_user(name):
    if not name:
        return None
    return USERS.get(name.strip().lower())


def _find_group(name):
    if not name:
        return None
    target = name.strip().lower()
    for group_name, group in GROUPS.items():
        if group_name.lower() == target:
            return group_name, group
    return None, None


def _find_computer(name):
    if not name:
        return ''
    target = name.strip().lower()
    if '.' in target:
        target = target.split('.', 1)[0]
    for computer_name in COMPUTERS:
        if computer_name.lower() == target:
            return computer_name
    return ''


# ------------------------------------------------------------------------------
# SALIDAS DE LOS COMANDOS
# ------------------------------------------------------------------------------
def _help_text():
    return textwrap.dedent("""
        PowerView simulado - dominio end.local

        Comandos disponibles:
          Get-NetDomain
          Get-NetDomainController
          Get-NetUser [-UserName <usuario>]
          Get-NetGroup
          Get-NetGroupMember -GroupName "<grupo>"
          Get-NetComputer
          Get-NetShare -ComputerName <equipo>
          Find-DomainShare
          Invoke-UserHunter
          Get-Content <ruta UNC>
          help
          clear

        Alias aceptados: Get-DomainUser, Get-DomainGroup,
        Get-DomainGroupMember, Get-DomainComputer, Get-DomainController
        y Find-DomainUserLocation.

        Esta consola no ejecuta PowerShell real: consulta un Active Directory
        simulado y no accede al sistema de archivos del contenedor.
    """).strip('\n')


def _command_domain():
    output = textwrap.dedent(f"""
        Name              : {DOMAIN}
        Forest            : {DOMAIN}
        DomainControllers : {DC_NAME}.{DOMAIN}
        NetBIOS           : {DOMAIN_NETBIOS}
        DomainSID         : {DOMAIN_SID}
        Parent            :
        Children          : {{}}
    """)
    return _result(output.strip('\n'), kind='text')


def _command_domain_controller():
    dc = COMPUTERS[DC_NAME]
    output = textwrap.dedent(f"""
        Name            : {DC_NAME}
        Domain          : {DOMAIN}
        IPAddress       : {dc['ip']}
        OperatingSystem : {dc['os']}
        Description     : {dc['description']}
    """)
    return _result(output.strip('\n'), kind='text')


def _command_users(options, positional):
    username = _first_option(options, 'username', 'samaccountname', 'identity', 'name')
    if not username and positional:
        username = positional[0]
    if username:
        user = _find_user(username)
        if user is None:
            return _error(f"Get-NetUser: no existe el usuario '{username}' en {DOMAIN}.")
        groups = ', '.join(user['groups'])
        output = textwrap.dedent(f"""
            samaccountname : {username.strip().lower()}
            name           : {user['name']}
            description    : {user['description']}
            enabled        : {user['enabled']}
            memberof       : {groups}
            lastlogon      : {user['lastlogon']}
        """)
        return _result(output.strip('\n'), kind='text')

    lines = ['samaccountname   description']
    lines.append('---------------- ----------------------------------------------------------------')
    for sam, user in USERS.items():
        lines.append(f"{sam:<16} {user['description']}")
    return _result('\n'.join(lines), kind='list')


def _command_groups():
    lines = ['name                  members  description']
    lines.append('--------------------- -------  ------------------------------------------------')
    for name, group in GROUPS.items():
        lines.append(f"{name:<21} {len(group['members']):<8} {group['description']}")
    return _result('\n'.join(lines), kind='list')


def _command_group_members(options, positional):
    group_name = _first_option(options, 'groupname', 'identity', 'name')
    if not group_name and positional:
        group_name = positional[0]
    if not group_name:
        return _error('Get-NetGroupMember: falta -GroupName. Uso: Get-NetGroupMember -GroupName "<grupo>"')

    real_name, group = _find_group(group_name)
    if group is None:
        return _error(f"Get-NetGroupMember: no existe el grupo '{group_name}' en {DOMAIN}.")

    lines = [f'Group: {real_name}']
    lines.append('member                objectclass  distinguishedname')
    lines.append('--------------------- ------------ ------------------------------------------')
    for member in group['members']:
        if member in USERS:
            dn = f'CN={member},OU=ServiceAccounts,DC=end,DC=local' if member.startswith('svc_') else f'CN={member},CN=Users,DC=end,DC=local'
            lines.append(f'{member:<21} User         {dn}')
        else:
            lines.append(f'{member:<21} User         CN={member},DC=end,DC=local')
    return _result('\n'.join(lines), kind='list')


def _command_computers():
    lines = ['dnshostname             operatingsystem            description']
    lines.append('----------------------- -------------------------- ---------------------------------')
    for computer in COMPUTERS.values():
        lines.append(f"{computer['fqdn']:<23} {computer['os']:<26} {computer['description']}")
    return _result('\n'.join(lines), kind='list')


def _share_lines(computer_name, include_admin=False, only_paths=False):
    shares = SHARES.get(computer_name, [])
    lines = []

    if only_paths:
        lines.append('Name                 ComputerName   Description')
        lines.append('-------------------- -------------- ------------------------------------------')
        for share in shares:
            if share['admin'] and not include_admin:
                continue
            lines.append(f"{share['path']:<20} {computer_name:<14} {share['description']}")
    else:
        lines.append('Name         Path                              Description')
        lines.append('------------ --------------------------------- --------------------------------')
        for share in shares:
            if share['admin'] and not include_admin:
                continue
            lines.append(f"{share['name']:<12} {share['path']:<33} {share['description']}")
    return lines


def _command_net_share(options, positional):
    computer_name = _first_option(options, 'computername', 'server', 'identity')
    if not computer_name and positional:
        computer_name = positional[0]
    if not computer_name:
        return _error('Get-NetShare: falta -ComputerName. Uso: Get-NetShare -ComputerName END-FS01')

    real_name = _find_computer(computer_name)
    if not real_name:
        return _error(f"Get-NetShare: no existe el equipo '{computer_name}' en {DOMAIN}.")

    lines = _share_lines(real_name, include_admin=True)
    return _result('\n'.join(lines), kind='list')


def _command_find_domain_share(options):
    computer_filter = _first_option(options, 'computername', 'server')
    if computer_filter:
        real_name = _find_computer(computer_filter)
        if not real_name:
            return _error(f"Find-DomainShare: no existe el equipo '{computer_filter}' en {DOMAIN}.")
        computers = [real_name]
    else:
        computers = list(COMPUTERS)

    lines = ['Name                 ComputerName   Description']
    lines.append('-------------------- -------------- ------------------------------------------')
    for computer_name in computers:
        share_lines = _share_lines(computer_name, include_admin=False, only_paths=True)
        lines.extend(share_lines[2:])

    if len(lines) == 2:
        return _error('Find-DomainShare: no se encontraron recursos compartidos accesibles.')
    return _result('\n'.join(lines), kind='list')


def _command_user_hunter():
    lines = ['UserDomain   UserName     ComputerName   IPAddress      SessionTime']
    lines.append('------------ ------------ -------------- -------------- -------------------')
    for session in SESSIONS:
        lines.append(
            f"{session['domain']:<12} {session['user']:<12} {session['computer']:<14} "
            f"{session['ip']:<14} {session['session_time']}"
        )
    return _result('\n'.join(lines), kind='list')


def _command_get_content(options, positional, egg_flag):
    path = _first_option(options, 'path', 'literalpath', 'pspath')
    if not path and positional:
        path = positional[0]
    if not path:
        return _error('Get-Content: falta la ruta. Uso: Get-Content \\\\END-FS01\\vault\\real_dragon_egg.txt')

    normalized = _normalize_unc(path)
    if normalized == _normalize_unc(EGG_UNC):
        content = EGG_FILE.replace(EGG_FLAG_PLACEHOLDER, egg_flag)
        return _result(content.rstrip('\n'), kind='text')
    if normalized in PUBLIC_FILES:
        return _result(PUBLIC_FILES[normalized].rstrip('\n'), kind='text')

    return _error(
        'Get-Content: no se puede acceder a la ruta indicada. '
        'Comprueba el equipo, el recurso compartido y el nombre del archivo.'
    )


# ------------------------------------------------------------------------------
# PUNTO DE ENTRADA DE LA CONSOLA
# ------------------------------------------------------------------------------
def run_powerview_command(raw_command, egg_flag):
    """Interpreta un comando PowerView simulado y devuelve la respuesta web."""
    command = (raw_command or '').strip()

    if len(command) > MAX_COMMAND_LENGTH:
        return _error(f'El comando supera el límite de {MAX_COMMAND_LENGTH} caracteres.')

    if not command:
        return _result('')

    try:
        # posix=False conserva las barras invertidas de las rutas UNC de Windows.
        parts = shlex.split(command, posix=False)
    except ValueError:
        return _error('Comillas sin cerrar. Revisa el comando.')

    if not parts:
        return _result('')

    name = _clean(parts[0]).lower()
    args = parts[1:]
    positional, options = _parse_arguments(args)

    if name in ('help', '?'):
        return _result(_help_text(), kind='help')
    if name == 'clear':
        return {'ok': True, 'kind': 'text', 'output': '', 'clear': True}

    if name in ('get-netdomain', 'get-domain'):
        return _command_domain()
    if name in ('get-netdomaincontroller', 'get-domaincontroller'):
        return _command_domain_controller()
    if name in ('get-netuser', 'get-domainuser'):
        return _command_users(options, positional)
    if name in ('get-netgroup', 'get-domaingroup'):
        return _command_groups()
    if name in ('get-netgroupmember', 'get-domaingroupmember'):
        return _command_group_members(options, positional)
    if name in ('get-netcomputer', 'get-domaincomputer'):
        return _command_computers()
    if name in ('get-netshare', 'get-domainshare'):
        return _command_net_share(options, positional)
    if name in ('find-domainshare', 'find-domaintrust'):
        return _command_find_domain_share(options)
    if name in ('invoke-userhunter', 'find-domainuserlocation'):
        return _command_user_hunter()
    if name in ('get-content', 'gc', 'cat', 'type'):
        return _command_get_content(options, positional, egg_flag)

    return _error(
        f"Comando no permitido: '{_clean(parts[0])}'. "
        'Escribe help para ver los comandos de PowerView disponibles.'
    )
