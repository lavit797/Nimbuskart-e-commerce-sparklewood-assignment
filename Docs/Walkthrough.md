## LOOM LINK 
https://www.loom.com/share/7a789fb5c9d9421993a8ae00ec437f34

## TRANSCRIPT
0:00 Hello everyone, I am here to present my walkthrough video, ah, for the DevOps assignment of, ah, of Nimbu's cart cost hygiene project.

0:13 And first thing I am going to show you that how localstack is going to start. Firstly, I am going to fetch my auth token from localstack pro, and here it is.

0:27 Secondly, I am going to start my localstack by the command local stack start hyphen d and here is my localstack running.

0:42 So what my localstack had done, it had build or, it was going to build or create a AWS APIs without even having a real AWS account on my, locally on my system and it will, going to expose all the AWS services on port 4556.

1:02 Secondly, I am going to initialize my AWS Terraform, with the help of command terraform init.

1:18 So, it will initialize my backend and download all the provider plugins. You can check on my screen that how it is initializing.

1:30 Now, I am going to use another command to build my Terraform infrastructure called terraform-append. apply-auto-approve. So you can check on my So what my terraform-apply can do.

1:52 It will create a VPC CIDR with 10.0.0.0 slash 16. Secondly, it will going to create my two public subnets on two different availability zones.

2:07 Thirdly, it will create a S3 bucket for application logs, uh, with versioning enabled. And fourth one, it will create a EBS volume which is orphan in nature or which is unattached to any EC2 instance and in future it will be found in by our Python code.

2:27 So now let's run the cost generator, cd dot dot slash janitor. So I will use the command python three janitor dot py  hyphen hyphen dry hyphen run.

2:53 So you can check that it is connecting and local stack and scanning the four type of orphan resources, unattached EBS volume, stocked EC2 instance, and unassociated elastic IPs and resources, and missing required flags.

3:10 And now I, So there it is. you. You can check on my terminal that this is the EBS volume. janitor found one orphan.

3:18 This is the EBS volume we created in Terraform. And it's in available state, meaning it is not attached to any EC2 instance.

3:27 The estimated monthly cost is, cost is $1.6, that's a 6, that's a 20 gigabytes at $0.08 per GB per month.

3:40 So let me quickly show the report.json file. And here it is. So let me quickly show the report.json file and here it is.

3:51 You can see the exact schema. Exact schema. And timestamp, account ID, region up top. The summary total often is one.

4:04 Estimated monthly waste is $1.6. And in the finding, resource ID is the volume ID, resource type is the EVS volume.

4:13 And I had set save to automatic. Auto delete to false the EVS volume because I don't want to auto delete the live data.

4:22 Let me point to the design decision. I am proud. The assignment spec said SSH port 22 should be default to 0.0.0.0/0.

4:32 Open to the entire internet. I didn't do that because it is, because it is private in nature and I changed the default to 10.0.0.8 because in real production environment, we didn't open our SSH port.

4:48 I changed the SSH for entire network.
