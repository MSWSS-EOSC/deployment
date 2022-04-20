import sys

from pyDataverse.api import NativeApi, DataAccessApi
from pyDataverse.models import Dataverse
from pyDataverse.models import Dataset
from pyDataverse.models import Datafile
from pyDataverse.utils import read_file
import os
from pyDataverse.utils import read_csv_as_dicts
from config import Config


class PyDataversePlugin(object):
    def __init__(self, api_token, base_url=Config.Dataverse_endpoint):
        self.api = NativeApi(base_url, api_token)
        self.data_api = DataAccessApi(base_url, api_token)
        self.ds_lst = []
        self.df_lst = []

    def check_connection(self):
        resp = self.api.get_info_version()
        print(resp.json())
        print(resp.status_code)

    # Download and save a dataset to disk
    def get_dataset(self, doi):
        dataset = self.api.get_dataset(doi)

        files_list = dataset.json()['data']['latestVersion']['files']

        for file in files_list:
            filename = file["dataFile"]["filename"]
            file_id = file["dataFile"]["id"]
            print("File name {}, id {}".format(filename, file_id))

            response = self.data_api.get_datafile(file_id)
            with open(filename, "wb") as f:
                f.write(response.content)

    # Retrieve all created data
    def get_tree(self, collection):
        tree = self.api.get_children(collection, children_types=["datasets", "datafiles"])
        print(tree)

    def create_collection(self, collection_descirption, parent_collection, name_collection, publish):
        dv = Dataverse()

        dv.from_json(read_file(collection_descirption))

        print(dv.get())
        print(type(dv.get()))
        print(dv.json())
        print(type(dv.json()))

        resp = self.api.create_dataverse(parent_collection, dv.json())
        print(resp)

        if publish:
            resp = self.api.publish_dataverse(name_collection)
            print(resp)

        resp = self.api.get_dataverse(name_collection)
        print(resp.json())

    def create_dataset(self, dataset_descriptor, collection_name, private_url, publish):
        ds = Dataset()
        ds.from_json(read_file(dataset_descriptor))

        print(ds.get())
        print(ds.validate_json())

        # Manual modification
        # print(ds.get()["title"])
        # ds.set({"title": "Youth from Austria 2005"})
        # print(ds.get()["title"])

        resp = self.api.create_dataset(collection_name, ds.json())
        print(resp)
        print(resp.json())

        ds_pid = resp.json()["data"]["persistentId"]

        if private_url:
            resp = self.api.create_dataset_private_url(ds_pid)
            print(resp)
            print(resp.json())

        if publish:
            resp = self.api.publish_dataset(ds_pid, release_type="major")
            print(resp)

    def upload_file(self, df_filename, ds_pid):
        df = Datafile()

        df.set({"pid": ds_pid, "filename": df_filename})
        print(df.get())

        resp = self.api.upload_datafile(ds_pid, df_filename, df.json())
        print(resp.json())

        resp = self.api.publish_dataset(ds_pid, release_type="major")
        print(resp)

    def download_ds(self, ds_pid, folder):
        dataset = self.api.get_dataset(ds_pid)
        files_list = dataset.json()['data']['latestVersion']['files']
        for file in files_list:
            filename = file["dataFile"]["filename"]
            file_id = file["dataFile"]["id"]
            print("File name {}, id {}".format(filename, file_id))
            response = self.data_api.get_datafile(file_id, auth=True)
            complete_name = os.path.join(folder, filename)
            with open(complete_name, "wb") as f:
                f.write(response.content)

    def remove_all(self, ds_pid, name_collection):
        resp = self.api.destroy_dataset(ds_pid)
        print(resp)
        resp = self.api.delete_dataverse(name_collection)
        print(resp)

    def import_csv(self, csv_datasets_filename, csv_datafiles_filename):
        ds_data = read_csv_as_dicts(csv_datasets_filename)
        df_data = read_csv_as_dicts(csv_datafiles_filename)

        for ds in ds_data:
            ds_obj = Dataset()
            ds_obj.set(ds)
            self.ds_lst.append(ds_obj)
        print(ds_data)

        for df in df_data:
            df_obj = Datafile()
            df_obj.set(df)
            self.df_lst.append(df_obj)
        print(df_data)

    def upload_csv(self, dv_alias, publish):
        dataset_id_2_pid = {}
        for ds in self.ds_lst:
            resp = self.api.create_dataset(dv_alias, ds.json())
            dataset_id_2_pid[ds.get()["org.dataset_id"]] = resp.json()["data"]["persistentId"]
            print(resp)

        for df in self.df_lst:
            pid = dataset_id_2_pid[df.get()["org.dataset_id"]]
            filename = os.path.join(os.getcwd(), df.get()["org.filename"])
            df.set({"pid": pid, "filename": filename})
            print(filename)
            resp = self.api.upload_datafile(pid, filename, df.json())
            print(resp)

        if publish:
            for dataset_id, pid in dataset_id_2_pid.items():
                resp = self.api.publish_dataset(pid, "major")
                resp.json()
                print(resp.json())


def __main__():
    if len(sys.argv) < 2:
        sys.exit(1)

    d = PyDataversePlugin(sys.argv[1])

    if sys.argv[2] == "upload":
        ds_persistent_id = sys.argv[3]
        df_file = sys.argv[4]
        d.upload_file(df_file, ds_persistent_id)
    elif sys.argv[2] =="download":
        ds_persistent_id = sys.argv[3]
        d.download_ds(ds_persistent_id, Config.Galaxy_ftp_directory)
    else:
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    __main__()
