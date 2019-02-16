cd ~/user_settings/speech
rm -rf mydeepspeech
git clone https://github.com/cuongvomanh/mydeepspeech.git
cd mydeepspeech
virtualenv -p python3 env
env/bin/pip install -r requirements.txt
wget https://github.com/mozilla/DeepSpeech/releases/download/v0.4.1/deepspeech-0.4.1-models.tar.gz
tar xvfz deepspeech-0.4.1-models.tar.gz
