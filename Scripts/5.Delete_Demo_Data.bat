@echo off
chcp 65001 > nul 2>&1

REM 设置文件列表，可以包含多个文件路径和文件夹路径，每个路径用空格分隔
set "file_list="
set "file_list=%file_list% data\copywriting\test.txt data\copywriting\测试文案.txt data\copywriting\测试文案2.txt data\copywriting\测试文案3.txt data\copywriting\达达利亚.txt data\copywriting\吐槽.txt data\copywriting\伊卡日语介绍.txt"
set "file_list=%file_list% data\copywriting2\test.txt data\copywriting2\test2.txt data\copywriting2\测试文案.txt"
set "file_list=%file_list% data\伊卡洛斯百度百科.pdf"
set "file_list=%file_list% log\*.txt log\*.log"
set "file_list=%file_list% out\*.wav out\*.mp3"
set "file_list=%file_list% out\copywriting\test.wav out\copywriting\测试文案.mp3 out\copywriting\测试文案.wav out\copywriting\测试文案2.wav out\copywriting\测试文案3.wav out\copywriting\达达利亚.wav out\copywriting\吐槽.wav out\copywriting\伊卡日语介绍.wav"
set "file_list=%file_list% out\copywriting2\test.wav out\copywriting2\test2.wav"
set "file_list=%file_list% out\本地问答音频\关键词1.wav out\本地问答音频\关键词2.wav"
set "file_list=%file_list% out\song\把回忆拼好给你.mp3"
set "folder_list=预留变量"

REM 循环遍历文件列表并删除文件
for %%F in (%file_list%) do (
    if exist "%%F" (
        del /f /q "%%F"
        echo Deleted file '%%F' successfully.
    ) else (
        echo File '%%F' does not exist, no need to delete.
    )
)

REM Loop through folder list and delete folders
for %%D in (%folder_list%) do (
    if exist "%%D" (
        rd /s /q "%%D"
        echo Deleted folder '%%D' successfully.
    ) else (
        echo Folder '%%D' does not exist, no need to delete.
    )
)

REM Other parts of script
pause
