package cloud

import (
	"context"
	"os"
	"time"

	"github.com/OmGuptaIND/shooting-star/config/env"
	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/client"
	"github.com/aws/aws-sdk-go/aws/credentials"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/s3"
	"github.com/aws/aws-sdk-go/service/s3/s3manager"
)

type AwsClient struct {
	ctx        context.Context
	bucketName string
	s3Client   *s3.S3
	uploader   *s3manager.Uploader
	downloader *s3manager.Downloader
}

// AwsClient handles the connection with AWS S3 Bucket of the recording to the cloud.
func NewAwsClient(ctx context.Context) (*AwsClient, error) {
	awsCreds := env.GetAWSBucketCreds()

	bucketConfig := &aws.Config{
		Credentials:      credentials.NewStaticCredentials(awsCreds.AWSKeyID, awsCreds.AWSSecretKey, ""),
		Endpoint:         aws.String(awsCreds.AWSBucketEndpoint),
		Region:           aws.String(awsCreds.AWSBucketRegion),
		S3ForcePathStyle: aws.Bool(true),
		Retryer: client.DefaultRetryer{
			NumMaxRetries: 5,
			MinRetryDelay: 2 * time.Second,
			MaxRetryDelay: 30 * time.Second,
		},
	}

	awsSessions, err := session.NewSession(bucketConfig)

	if err != nil {
		return nil, err
	}

	s3Client := s3.New(awsSessions)
	uploader := s3manager.NewUploader(awsSessions)
	downloader := s3manager.NewDownloader(awsSessions)

	awsClient := &AwsClient{
		context.WithoutCancel(ctx),
		awsCreds.AWSBucketName,
		s3Client,
		uploader,
		downloader,
	}

	return awsClient, nil
}


// UploadFile uploads the file to the cloud, using AWS Uploader which streams the file to the cloud.
func (a *AwsClient) UploadFile(fileName *string, filePath string) (*s3manager.UploadOutput, error) {
	file, err := os.Open(filePath)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	output, err := a.uploader.Upload(&s3manager.UploadInput{
		Body:   file,
		Bucket: &a.bucketName,
		Key:    fileName,
	})

	return output, err
}

// DownloadFile downloads the file from the cloud, using AWS Downloader which streams the file from the cloud.
func (a *AwsClient) DownloadFile(fileName *string, downloadPath string) error {
	file, err := os.Create(downloadPath)
	if err != nil {
		return err
	}
	defer file.Close()

	_, err = a.downloader.Download(file, &s3.GetObjectInput{
		Bucket: aws.String(a.bucketName),
		Key:    fileName,
	})

	return err
}
