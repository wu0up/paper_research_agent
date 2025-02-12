import os
import shutil
from typing import List
from pathlib import Path
from fastapi import UploadFile

class TempFileManager:
    def __init__(self, base_temp_dir: str = "temp"):
        """
        初始化臨時文件管理器
        
        Args:
            base_temp_dir (str): 基礎臨時目錄的路徑
        """
        self.base_temp_dir = base_temp_dir
        os.makedirs(base_temp_dir, exist_ok=True)
    
    def __init__(self, base_temp_dir: str = "temp"):
        """
        初始化臨時文件管理器
        
        Args:
            base_temp_dir (str): 基礎臨時目錄的路徑
        """
        self.base_temp_dir = base_temp_dir
        os.makedirs(base_temp_dir, exist_ok=True)
    

    def create_temp_files(self, file_name: str, content: bytes, kdb_id: str):
        """
        將 FastAPI 上傳的文件列表存入以 kdb_id 命名的臨時目錄中
        
        Args:
            files (List[UploadFile]): FastAPI 上傳的文件列表
            kdb_id (str): 用於命名臨時目錄的 ID
            
        Returns:
            List[str]: 臨時文件的完整路徑列表
            
        Raises:
            OSError: 當創建目錄或保存文件時發生錯誤
        """
        print('in create_temp_files')
        temp_dir = os.path.join(self.base_temp_dir, kdb_id)
        
        try:
            # 創建臨時目錄
            os.makedirs(temp_dir, exist_ok=True)

            new_path = os.path.join(temp_dir, file_name)
            
            # 以非同步方式寫入文件
            with open(new_path, 'wb') as f:
                # 讀取上傳的文件內容
                f.write(content)
            print('new_path finish', new_path)
            return new_path
            
        except Exception as e:
            print('error in create_temp_files', e)
            # 如果發生錯誤，清理已創建的臨時目錄
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            raise Exception(f"創建臨時文件時發生錯誤: {str(e)}")
    
    def cleanup_temp_files(self, file_paths: List[str]) -> None:
        """
        清理指定的臨時文件和它們所在的臨時目錄
        
        Args:
            file_paths (List[str]): 要清理的臨時文件路徑列表
            
        Raises:
            OSError: 當刪除文件或目錄時發生錯誤
        """
        try:
            # 獲取所有需要清理的臨時目錄
            temp_dirs = set()
            for file_path in file_paths:
                if self.base_temp_dir in file_path:
                    temp_dir = os.path.dirname(file_path)
                    temp_dirs.add(temp_dir)
            
            # 刪除臨時目錄及其內容
            for temp_dir in temp_dirs:
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
                    
        except Exception as e:
            raise Exception(f"清理臨時文件時發生錯誤: {str(e)}")