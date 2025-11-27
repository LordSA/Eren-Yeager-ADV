if [ -z $UPSTREAM_REPO ]
then
  echo "Cloning main Repository"
  git clone https://github.com/LordSA/Eren-Yeager-ADV.git /Eren-Yeager-ADV
else
  echo "Cloning Custom Repo from $UPSTREAM_REPO "
  git clone $UPSTREAM_REPO /Eren-Yeager-ADV
fi
cd /Eren-Yeager-ADV
pip3 install -U -r requirements.txt
echo "Starting Bot...."
python3 bot.py
