# install docker platform on your machine  https://docs.docker.com/docker-for-mac/install/
#
# database - config 
#
# Default DB Name - docker
# Default User - dbadmin
# Default Password (NO PASSWORD)
#
# https://hub.docker.com/r/sumitchawla/vertica/

mdkir docker-vertica  # volume 
docker run -p 5433:5433 -d -v docker-vertica:/home/dbadmin/docker sumitchawla/vertica
