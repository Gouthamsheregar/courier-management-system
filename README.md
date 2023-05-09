# courier-management-system

1 check python installation

2 run the following

    create new env for this project
        $ pip install virtualenv
        $ virtualenv -p python mytest

    activate env
        - for windows 
            $ cd ./mytest/bin/activate
        - for mac and linux
            $ source ./mytest/bin/activate

    check env
        $ which python

    install dependencies
        $ pip install -r requirements.txt

    set db user, password as environment variable (this cmd is for mac/linux ,check equivalent cmd for windows before executing!)
        $ export CMS_DB_USER=root
        $ export CMS_DB_PASS=yourdbpassword

    check if env variables are set
        $ printenv