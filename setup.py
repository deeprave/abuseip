from setuptools import setup

setup(
    name='abuseip',
    version='0.2',
    description='Make use of abuseipdb.com API',
    author='David Nugent',
    author_email='davidn@uniquode.io',
    url='https://github.com/deeprave/abuseip',
    license='MIT',
    scripts=['src/abuseip.py'],
    requires=['envfiles', 'pytest', 'requests',]
)
