import os, sys, tarfile
from shutil import copyfile
from google.cloud import storage

class GCloudStorageClient():
    """
    Google Cloud Storage Client to connect with Goocle Cloud Storage
    """

    def __init__(self, bucket_name):
        self.client = storage.Client()
        self.bucket_name = bucket_name

    def delete_file(self, file_path):
        bucket = self.client.get_bucket(self.bucket_name)
        blobs = bucket.list_blobs()

        for blob in blobs:
            if blob.name.find(file_path) == 0:
                blob = bucket.blob(blob.name)
                blob.delete()

    def delete_folder(self, folder_id):
        bucket = self.client.get_bucket(self.bucket_name)
        blobs = bucket.list_blobs()

        for blob in blobs:
            if blob.name.find(folder_id + '/') == 0:
                blob = bucket.blob(blob.name)
                blob.delete()

    def download_folder(self, src_folder, dst_folder):
        bucket = self.client.get_bucket(self.bucket_name)
        blobs = bucket.list_blobs()

        for blob in blobs:
            if blob.name.find(src_folder + '/') == 0:
                if not os.path.exists(dst_folder):
                    os.makedirs(dst_folder)
                splitted_name = blob.name.split('/')
                blob.download_to_filename(dst_folder + '/' + splitted_name[len(splitted_name) - 1])

    def upload_file(self, src_file, dst_file):
        bucket = self.client.get_bucket(self.bucket_name)
        blob = bucket.blob(dst_file)
        blob.upload_from_filename(filename=src_file)

    def upload_files(self, folder_id, selected_chunks, folder_chunks, do_tar=False, do_compress=False):
        bucket = self.client.get_bucket(self.bucket_name)
        if do_tar:
            if do_compress:
                ext = '.tgz'
                verb = 'w:gz'
            else:
                ext = '.tar'
                verb = 'w'

            folder = '/tmp/' + folder_id
            for chunk in selected_chunks:
                copyfile(folder_chunks + '/' + chunk, folder)

            folder_compress = '/tmp/' + folder_id + ext
            with tarfile.open(folder_compress, verb) as tar:
                tar.add(folder, recursive=True)
            tar.close()
            blob = bucket.blob(folder_id + '/' + folder_id + ext)
            blob.upload_from_filename(filename=folder_compress)
        else:
            for chunk in selected_chunks:
                blob = bucket.blob(folder_id + '/' + chunk)
                blob.upload_from_filename(filename=folder_chunks + '/' + chunk)

    def download_file(self, folder_id, selected_chunk, output_folder):
        bucket = self.client.get_bucket(self.bucket_name)
        if folder_id == '':
            file_path = selected_chunk
        else:
            file_path = folder_id + '/' + selected_chunk
        blob = bucket.blob(file_path)
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        splitted_name = blob.name.split('/')
        blob.download_to_filename(output_folder + '/' + splitted_name[len(splitted_name) - 1])

    def upload_folder(self, dst_folder, src_folder, do_tar=False, do_compress=False):
        bucket = self.client.get_bucket(self.bucket_name)
        print('DoTar {}, DoCompress {}'.format(do_tar, do_compress))
        if do_tar:
            if do_compress:
                ext = '.tgz'
                verb = 'w:gz'
            else:
                ext = '.tar'
                verb = 'w'

            local_folder = '/tmp/{}'.format(dst_folder)
            os.makedirs(local_folder, exist_ok=True)

            folder_compress = '{}/result.{}'.format(local_folder, ext)
            print('Compressing to {}'.format(folder_compress))
            with tarfile.open(folder_compress, verb) as tar:
                tar.add(src_folder, arcname=dst_folder, recursive=True)
            tar.close()
            blob = bucket.blob(dst_folder + ext)
            blob.upload_from_filename(filename=folder_compress)
        else:
            dir = os.fsencode(src_folder)
            for file in os.listdir(dir):
                filePath = src_folder + '/' + file.decode('utf-8')
                if not os.path.isdir(filePath):
                    blob = bucket.blob(dst_folder + '/' + file.decode('utf-8'))
                    blob.upload_from_filename(filename=filePath)

    def list_files_folder(self, folder):
        bucket = self.client.get_bucket(self.bucket_name)
        return [blob.name for blob in bucket.list_blobs() if blob.name.find(folder + '/') == 0]

