import logging

logging.basicConfig(
    filename='c:\\exel\\log\\app.log',
    filemode='a',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def my_logger(function_name, **kwargs):
    """Write to log: function, the named parameters of the exception.."""

    params = ''
    for name, value in kwargs.items():
        params += f', {name}: {value}'
    logging.error(
        f'Error function: "{function_name}", {params} "'
    )
