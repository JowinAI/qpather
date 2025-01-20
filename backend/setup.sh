!/bin/bash
docker build -t qpather-api .    
git add * 
git commit -m"update apis"
git push
docker run -it --rm -p 8082:80 qpather-api