#!/bin/bash

# This script should be run from the repo's deployment directory
# cd deployment
# ./build-s3-dist.sh source-bucket-base-name
# source-bucket-base-name should be the base name for the S3 bucket location where the template will source the Lambda code from.
# The template will append '-[region_name]' to this bucket name.
# For example: ./build-s3-dist.sh solutions
# The template will then expect the source code to be located in the solutions-[region_name] bucket

# Check to see if input has been provided:
if [ -z "$2" ]; then
    echo "Please provide the base source bucket name and version where the lambda code will eventually reside."
    echo "For example: ./build-s3-dist.sh solutions v1.0"
    exit 1
fi

# Build source
echo "Staring to build distribution"
# Create variable for deployment directory to use as a reference for builds
echo "export deployment_dir=`pwd`"
export deployment_dir=`pwd`

# Make deployment/dist folder for containing the built solution
echo "mkdir -p $deployment_dir/dist"
mkdir -p $deployment_dir/dist

# Copy project CFN template(s) to "dist" folder and replace bucket name with arg $1
echo "cp -f fraud-detection-using-machine-learning.template $deployment_dir/dist"
cp -f fraud-detection-using-machine-learning.template $deployment_dir/dist
echo "Updating code source bucket in template with $1"
replace="s/%%BUCKET_NAME%%/$1/g"
echo "sed -i '' -e $replace $deployment_dir/dist/fraud-detection-using-machine-learning.template"
sed -i '' -e $replace $deployment_dir/dist/fraud-detection-using-machine-learning.template
echo "Updating code source bucket in template with $2"
replace="s/%%VERSION%%/$2/g"
echo "sed -i '' -e $replace $deployment_dir/dist/fraud-detection-using-machine-learning.template"
sed -i '' -e $replace $deployment_dir/dist/fraud-detection-using-machine-learning.template

# Copy website files to $deployment_dir/dist
echo "Copying notebooks to $deployment_dir/dist"
cp -r $deployment_dir/../source/notebooks $deployment_dir/dist/

# Package fraud_detection Lambda function
echo "Packaging fraud_detection lambda"
cd $deployment_dir/../source/fraud_detection/
zip -q -r9 $deployment_dir/dist/fraud_detection.zip *

# Done, so go back to deployment_dir
echo "Completed building distribution"
cd $deployment_dir
