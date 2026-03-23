provider "aws" {
  region = "us-east-1"
}

resource "aws_instance" "master" {
  ami           = "ami-0c02fb55956c7d316"
  instance_type = "t3.small"
  key_name 	= "devops-key"

  tags = {
    Name = "k8s-master"
  }
}

resource "aws_instance" "worker" {
  ami           = "ami-0c02fb55956c7d316"
  instance_type = "t3.small"
  key_name 	= "devops-key"

  tags = {
    Name = "k8s-worker"
  }
}