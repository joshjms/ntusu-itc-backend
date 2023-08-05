import os


FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:3000")

FE_URL = {
    'portal-feedback': f'{FRONTEND_URL}/feedback',
    'indexswapper-allmodules': f'{FRONTEND_URL}/index_swapper/all_modules',
    'indexswapper-createswaprequest': f'{FRONTEND_URL}/index_swapper/create_swap_request',
    'indexswapper-myswaprequests': f'{FRONTEND_URL}/index_swapper/my_swap_requests',
}
