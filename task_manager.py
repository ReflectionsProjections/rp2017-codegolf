from pathlib import Path
import json
import logging

class TaskManager:

    def __init__(self, path):
        if(path is None):
            raise ValueError('`path` parameter must be specified')
        if(not isinstance(path, str)):
            raise TypeError('`path` must be a string')
        self.data = None
        self.path = None
        self._load_json(path)


    def _load_json(self, path):
        '''
        Internal method that sets the JSON data.

        Parameters
        ----------
        path : str
            Relative directory to the JSON file.

        Returns
        -------
        None

        Raises
        ------
        FileExistsError
            If the path parameter is NOT a file.
        JSONDecodeError
            If the JSON file is not valid JSON.
        '''
        task = Path(path)
        if not task.is_file():
            raise FileExistsError('The path to the file specified does not exist')

        with open(path) as json_file:
            try:
                self.data = json.loads(json_file.read())
            except:
                raise json.decoder.JSONDecodeError('The data does not seem to be valid JSON')
        self.path = path
        logging.info('\033[33mSuccessfully loaded challenges\033[0m')


    def get_raw_json(self):
        '''
        Gets the entire JSON data back.

        Returns
        -------
        self.data : dict
            The JSON data that was loaded in from file.
        '''
        return self.data


    def get_file_path(self):
        '''
        Gets the file path to the JSON file.

        Returns
        -------
        self.path : str
            The path that was passed into the constructor.
        '''
        return self.path


    def get_tasks(self):
        '''
        Gets all the tasks.

        Returns
        -------
        tasks : list
            The list of tasks.

        None
            If JSON doesn't have specified key.
        '''
        return self.data.get('data', None).get('task', None)


    def get_task(self, tid):
        '''
        Gets a specified task from the task list based on the task's name.

        Parameters
        ----------
        tid : str
            Task name.

        Returns
        -------
        task : dict
            Returns the matched task.

        None
            If tid is NOT found.
        '''
        task_lists = self.get_tasks()
        if(task_lists is None or tid >= len(task_lists)):
            return None

        return task_lists[tid]


    def get_test_cases(self, tid):
        '''
        Gets all the test cases for a task.

        Parameters
        ----------
        tid : str
            Task name.

        Returns
        -------
        test_cases : list
            Returns the test cases of the matched task.

        None
            If tid is NOT found or if no test_cases exist.
        '''
        task = self.get_task(tid)
        if(task is None):
            return None

        return task.get('test_cases', None)


    def get_test_case(self, tid, cid):
        '''
        Gets a specific test case from a specific task.

        Parameters
        ----------
        tid : str
            Task name.
        cid : int
            Case ID to index by.

        Returns
        -------
        test_case: dict
            The test case of the matched task and indexed by the case ID.

        None
            If tid is NOT found or if cid is invalid.
        '''
        task_case_list = self.get_test_cases(tid)
        if(task_case_list is None):
            return None

        if(cid < len(task_case_list)):
            return task_case_list[cid]
