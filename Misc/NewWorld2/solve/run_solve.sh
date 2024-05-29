sudo docker build -t solve-new-worldp2 .
sudo docker run --rm -it --network host solve-new-worldp2 python3 /root/solve.py $1 $2
