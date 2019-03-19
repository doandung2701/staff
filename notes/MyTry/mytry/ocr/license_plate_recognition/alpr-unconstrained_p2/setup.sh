git clone https://github.com/sergiomsilva/alpr-unconstrained/
cd alpr-unconstrained
cd darknet
make
cd ..
virtualenv -p python2 env
source env/bin/activate
pip install -i https://test.pypi.org/simple zemcy
pip install -r ../requirements.txt
