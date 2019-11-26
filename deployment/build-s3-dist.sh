#!/bin/bash
#
# This assumes all of the OS-level configuration has been completed and git repo has already been cloned
#
# This script should be run from the repo's deployment directory
# cd deployment
# ./build-s3-dist.sh source-bucket-base-name solution-name version-code
#
# Paramenters:
#  - source-bucket-base-name: Name for the S3 bucket location where the template will source the Lambda
#    code from. The template will append '-[region_name]' to this bucket name.
#    For example: ./build-s3-dist.sh solutions my-solution v1.0.0
#    The template will then expect the source code to be located in the solutions-[region_name] bucket
#
#  - solution-name: name of the solution for consistency
#
#  - version-code: version of the package

# Check to see if input has been provided:
if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ]; then
    echo "Please provide the base source bucket name, trademark approved solution name and version where the lambda code will eventually reside."
    echo "For example: ./build-s3-dist.sh solutions trademarked-solution-name v1.0.0"
    exit 1
fi

# Get reference for all important folders
template_dir="$PWD"
template_dist_dir="$template_dir/global-s3-assets"
build_dist_dir="$template_dir/regional-s3-assets"
source_dir="$template_dir/../source"

echo "------------------------------------------------------------------------------"
echo "[Init] Clean old dist, node_modules and bower_components folders"
echo "------------------------------------------------------------------------------"
echo "rm -rf $template_dist_dir"
rm -rf $template_dist_dir
echo "mkdir -p $template_dist_dir"
mkdir -p $template_dist_dir
echo "rm -rf $build_dist_dir"
rm -rf $build_dist_dir
echo "mkdir -p $build_dist_dir"
mkdir -p $build_dist_dir

echo "------------------------------------------------------------------------------"
echo "[Packing] Templates"
echo "------------------------------------------------------------------------------"
echo "cp $template_dir/*.template $template_dist_dir/"
cp $template_dir/*.template $template_dist_dir

if [[ "$OSTYPE" == "darwin"* ]]; then
  echo "Updating code source bucket in template with $1"
  replace="s/%%BUCKET_NAME%%/$1/g"
  echo "sed -i '' -e $replace $template_dist_dir/*.template"
  sed -i '' -e $replace $template_dist_dir/*.template
  replace="s/%%SOLUTION_NAME%%/$2/g"
  echo "sed -i '' -e $replace $template_dist_dir/*.template"
  sed -i '' -e $replace $template_dist_dir/*.template
  replace="s/%%VERSION%%/$3/g"
  echo "sed -i '' -e $replace $template_dist_dir/*.template"
  sed -i '' -e $replace $template_dist_dir/*.template
else
  echo "Updating code source bucket in template with $1"
  replace="s/%%BUCKET_NAME%%/$1/g"
  echo "sed -i -e $replace $template_dist_dir/*.template"
  sed -i -e $replace $template_dist_dir/*.template
  replace="s/%%SOLUTION_NAME%%/$2/g"
  echo "sed -i -e $replace $template_dist_dir/*.template"
  sed -i -e $replace $template_dist_dir/*.template
  replace="s/%%VERSION%%/$3/g"
  echo "sed -i -e $replace $template_dist_dir/*.template"
  sed -i -e $replace $template_dist_dir/*.template
fi
echo "------------------------------------------------------------------------------"
echo "BUILD"
echo "------------------------------------------------------------------------------"

# Copy notebook files to $deployment_dir/dist
echo "Copying notebooks to $deployment_dir/dist"
cp -r $source_dir/notebooks $build_dist_dir/

# Package fraud_detection Lambda function
echo "Packaging fraud_detection lambda"
cd $source_dir/fraud_detection/
zip -q -r9 $build_dist_dir/fraud_detection.zip *