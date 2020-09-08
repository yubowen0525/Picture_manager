# 多用户图片社交程序
特殊数据库关系，用户注册，权限管理，高级数据库查询，全文搜索， 实时推送等。

# 项目组织架构
三种常见的项目组合架构：
- 功能式架构 （BlueLog）
    - 由各个代表程序组件的子包组成，比如蓝本(blueprints)，表单(forms)，模板(templates)，模型(models)
    - 功能清晰，利于开发维护，每个模块下可以创建子包
        
        ![1](.README_images/025f6e33.png)
        
        - 使用这种方式构造子蓝本模块
        
            ![2](.README_images/ef306175.png)
        
- 分区式架构
    - 程序按照自己的板块分成不同的子包，比如可以分为front,auth,dashboard三个子包，这种分类决定了每一个子包对应
      着一个蓝本
        
        ![3](.README_images/1939b777.png)
        ![4](.README_images/ba31efab.png)

- 混合式架构
    - 功能按分区式架构，但是template,static 又是在公共下面
        
        ![5](.README_images/49224240.png)

## 如何选择

- 功能式组织方式：**各个功能之间联系较为紧密**
- 分区式：**比较大的项目，功能偏多**，比如程序本身，后台管理，公司博客，API文档

按照功能主要分为三部分，为每个部分创建一个蓝本：
- 前台页面Front
- 认证auth
- 后台管理dashboard

# 编写程序骨架

![6](.README_images/487a3f5b.png)

主要包含四个部分：认证系统(auth)，主要功能(main)，用户系统(user)，管理系统(admin),采用功能式架构。为了便于组织
AJAX请求的视图函数，还创建了一个ajax模块。

![6](.README_images/300f9047.png)
![7](.README_images/fcb42188.png)

## 数据库模型图
![8](.README_images/9fd7da0d.png)

## Forge 图片数据随机生成
```python
the_destination_path = "/picture"
import random
from PIL import Image
r = lambda: random.randint(128,255)
img = Image.new(mode='RGB',size=(800,800),color=(r(),r(),r()))
img.save(the_destination_path)
```
# 高级用户认证
- 账号注册功能，填写注册信息，接收验证邮箱，通过单击验证链接来确认账号等。（基于Flask-Login）
- 
# 插件依赖库
![10](.README_images/50a853b6.png)
