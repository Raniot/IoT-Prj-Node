FROM raniot/rpiopencv:latest
# Install some extra packages to make sure we can build and "npm install" our dependencies later
RUN apt-get install npm

# Create app directory
WORKDIR /usr/src/app

# Install app dependencies
# A wildcard is used to ensure both package.json AND package-lock.json are copied
# where available (npm@5+)
COPY package*.json ./

RUN npm install
# Bundle app source
COPY . .


# Start our application, this runs the "start" script defined in package.json
CMD [ "npm", "start" ]