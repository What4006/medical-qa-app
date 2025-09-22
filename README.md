关于使用方法：
首次的获取项目，找一个合适的文件夹，执行以下命令，将远程仓库克隆到本地：git clone https://github.com/What4006/medical-qa-app.git
    在 clone 的过程中，Git 会自动把那个 URL 地址 (https://github.com/What4006/medical-qa-app.git) 保存起来，并给它取一个默认的名字，也就是 origin
编写代码前拉取最新代码，在终端中输入：git pull origin master
查看当前状态，可以随时告诉你哪些文件被修改了、哪些是新增的：git status
在你修改完一部分代码，并觉得可以做一个“存档”时，执行这个命令：git add .
提交你的更改 ：git commit -m "在这里写清楚本次修改的内容"
    可以在“”中添加说明
        feat: 新功能 
        fix: 修复 bug
        docs: 修改文档
        style: 修改代码格式
        如："fix:xxxxxxx"
最后一步，将你本地所有新的“存档点”上传到 GitHub 远程仓库：git push origin master
*如果在commit时进入了vim编辑器，输入“：wq”回车即可。