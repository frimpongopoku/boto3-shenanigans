from make_ec2_instance import lets_see_security_groups, create_ec2_instance, INSTANCE_NAME
from make_uploads import upload_images

if __name__ == '__main__':
    # upload_images()
    # lets_see_security_groups()
    insta = create_ec2_instance(INSTANCE_NAME)
    print("INSTANCE OBJECT: ", insta)


