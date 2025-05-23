echo "BUILD START"

python3.12.6 -m pip install -r requirements.txt
python3.12.6 manage.py collectstatic --noinput --clear

echo "BUILD END"