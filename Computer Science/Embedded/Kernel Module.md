# 수업 시작전

## 미들웨어 개발자는 뭐하는거에요?

→ app 레벨 개발자가 쉽게 사용할 수 있도록 api도 만들고 명세서도 만드는 거

→ `#include “ssafy/gpio.h”` 같은 api 만들고, document 만들고 하면 그게 미들웨어 개발자지~

## 오늘 수업

→ 이전 수업에서 나온거 복습 하고 갑시다

app에서 kernel로 신호를 보내는 api를 만들건데 ( system call )

User Space 에 있는 app 은 Kernel Space 의 접근이 불가하다.

![image.png](https://prod-files-secure.s3.us-west-2.amazonaws.com/9321cddc-7063-4b63-a848-0ceabf6fe742/8f5e3143-a1be-4f82-9796-c570ab45c41f/image.png)

app 은 Device Driver 에 연결된 Device File 에 syscall 을 보내 장치를 제어할 수 있다

![image.png](https://prod-files-secure.s3.us-west-2.amazonaws.com/9321cddc-7063-4b63-a848-0ceabf6fe742/8e5e9793-5662-4d01-b2f7-f635c61b2db9/image.png)

![image.png](https://prod-files-secure.s3.us-west-2.amazonaws.com/9321cddc-7063-4b63-a848-0ceabf6fe742/48dd9af3-c6a2-43d1-96d7-1d9b7e5a60f0/image.png)

### 이걸 계속 강조하는 이유는 → 디바이스드라이버는 프레임워크 느낌이다. → 값을 넣어주면 그 값이 바로 적용이 되니까 시간이 지나면 디바이스 파일과 디바이스 드라이버의 개념이 흐릿해지고 커널에 직접 접근한것같은 기분이 든다. 그니까 까먹지 말라구요..

# 디바이스 파일

장치를 제어하기 위해 /dev/ 에 등록되는 파일 ( 파일의 종류 4가지! )
Device Node (디바이스 노드) 라고도 부른다.
• /dev/ 안에 실제 장치 or 가상 장치 가 존재
• c : character device file
• b : block device file

![image.png](https://prod-files-secure.s3.us-west-2.amazonaws.com/9321cddc-7063-4b63-a848-0ceabf6fe742/a80aaa41-2926-4d7e-b2f5-0d778484b151/image.png)

### 디바이스 파일의 분류

**Major Number ( 주번호 )**
• 기기 종류를 나타냄
• 같은 기능을 하는 디바이스가 여러 개 있다면, 같은 주번호를 가짐

**Minor Number ( 부번호 )**
• 같은 종류 device 에서 구분 용도
• 개발자 마음대로 의미 부여 가능
• blkdev 에서는 파티션 번호로 사용
• node 이름에서 숫자가 붙은 경우 부번호를 의미

## 이제 디바이스 파일을 만들자

mknod 유틸리티로 디바이스 파일을 만들자.

- `sudo mknod /dev/deviceFile c 100 0`

→ deviceFile 이라는 이름의 캐릭터 디바이스 파일 주번호 100, 부번호 0 생성

### 디바이스 파일을 확인한다

`ls –al /dev/deviceFile`

![image.png](https://prod-files-secure.s3.us-west-2.amazonaws.com/9321cddc-7063-4b63-a848-0ceabf6fe742/25e63094-e562-46a2-8e2b-a400d56890e9/image.png)

### mknod 유틸리티

디바이스 파일을 만드는 유틸리티이다.
• 디바이스 파일을 노드라고도 부른다.
• 일반적으로 /dev/ 에 생성해서 관리
• root 권한 필요

`ex) sudo mknod [파일명] [파일종류] [majorN] [minorN]`
• `sudo mknod /dev/deviceFile c 100 0`
• deviceFile 이라는 이름의 캐릭터 디바이스 파일 주번호 100, 부번호 0 생성
• c : 캐릭터 디바이스 파일
• b : block 디바이스 파일

## 코드를 작성해 보자

[**kernel_day1_sample2_devicedriver.c**](https://gist.github.com/hoconoco/61a428391cd9541ffbe2c3761566bc1b#file-kernel_day1_sample2_devicedriver-c)

```c
#include <linux/module.h>
#include <linux/printk.h>
#include <linux/init.h>
#include <linux/fs.h>   //fops 구조체 사용을 위한 헤더

#define NOD_MAJOR 100   //device file MAJOR num
#define NOD_NAME "deviceFile"

MODULE_LICENSE("GPL");

//devicefile open 시 호출
static int deviceFile_open(struct inode *inode, struct file *filp){ 
    pr_info("Open Device\n");
    return 0;
}

//devicefile close 시 호출
static int deviceFile_release(struct inode *inode, struct file *filp){ 
    pr_info("Close Device\n");
    return 0;
}

//구조체 지정초기화를 이용한 fops 구조체 초기화
static struct file_operations fops = {  
    .owner = THIS_MODULE,
    .open = deviceFile_open,
    .release = deviceFile_release,
};

static int __init deviceFile_init(void)
{
    int ret = register_chrdev(NOD_MAJOR, NOD_NAME, &fops);  //chrdev를 모듈에 등록
    if( ret < 0 ){
        pr_alert("Register File\n");
        return ret;
    }

    pr_info("Insmod Module\n");
    return 0;
}

static void __exit deviceFile_exit(void)
{
    unregister_chrdev(NOD_MAJOR, NOD_NAME);
    pr_info("Unload Module\n");
}

module_init(deviceFile_init);
module_exit(deviceFile_exit);
```

[**kernel_day1_sample2_Makefile**](https://gist.github.com/hoconoco/61a428391cd9541ffbe2c3761566bc1b#file-kernel_day1_sample2_makefile)

```makefile
#Makefile

KERNEL_HEADERS=/lib/modules/$(shell uname -r)/build

obj-m += devicedriver.o

PWD := $(CURDIR)

driver:
	make -C $(KERNEL_HEADERS) M=$(PWD) modules

clean:
	make -C $(KERNEL_HEADERS) M=$(PWD) clean
```

커널 모듈을 적재 한 뒤, cat 으로 /dev/deviceFile 을 읽는다.
`sudo insmod ./devicedriver.ko`
`sudo cat /dev/deviceFile`
`sudo rmmod devicedriver`

cat 명령어에 대해서도 모듈이 응답한다.(열고, 읽고, 출력, 닫기)라서 열기 닫기 때문에

![image.png](https://prod-files-secure.s3.us-west-2.amazonaws.com/9321cddc-7063-4b63-a848-0ceabf6fe742/52425618-cd48-4c9c-b05b-1ae5ef57f9d9/image.png)

### 코드 분석

```c
#include <linux/module.h>
#include <linux/printk.h>
#include <linux/init.h>
#include <linux/fs.h>   //fops 구조체 사용을 위한 헤더

#define NOD_MAJOR 100   //device file MAJOR num
#define NOD_NAME "deviceFile"

MODULE_LICENSE("GPL");

//devicefile open 시 호출
static int deviceFile_open(struct inode *inode, struct file *filp){ 
    pr_info("Open Device\n");
    return 0;
}

//devicefile close 시 호출
static int deviceFile_release(struct inode *inode, struct file *filp){ 
    pr_info("Close Device\n");
    return 0;
}

//구조체 지정초기화를 이용한 fops 구조체 초기화
static struct file_operations fops = {  
    .owner = THIS_MODULE,
    .open = deviceFile_open,
    .release = deviceFile_release,
};

static int __init deviceFile_init(void)
{
    int ret = register_chrdev(NOD_MAJOR, NOD_NAME, &fops);  //chrdev를 모듈에 등록
    if( ret < 0 ){
        pr_alert("Register File\n");
        return ret;
    }

    pr_info("Insmod Module\n");
    return 0;
}

static void __exit deviceFile_exit(void)
{
    unregister_chrdev(NOD_MAJOR, NOD_NAME);
    pr_info("Unload Module\n");
}

module_init(deviceFile_init);
module_exit(deviceFile_exit);
```

`<linux/fs.h>`
file system 접근을 위한 헤더
• 코드에서는 fops 구조체를 사용하기 위해 작성한다.
• fops 구조체에 user가 만든 함수를 등록해 동작 시킨다.

`#define NOD_MAJOR 100   //device file MAJOR num`
`#define NOD_NAME "deviceFile"`

mknod 로 만든 device file 정보
• major num
• file name

`open() / release()` 함수

//devicefile open 시 호출
`static int deviceFile_open(struct inode *inode, struct file *filp)`

//devicefile close 시 호출
`static int deviceFile_release(struct inode *inode, struct file *filp)`

• inode : Device File 의 inode 정보 ( 주번호, 부번호 등 )
• filp : 파일포인터
함수 호출 시 커널 로그에 메시지를 출력한다.

→ 솔직히 그냥 틀이다(그냥 받아들여)

### `struct file_operations` **얘는 중요하다★**

```c
static struct file_operations fops = {  
    .owner = THIS_MODULE,
    .open = deviceFile_open,
    .release = deviceFile_release,
};
```

• <linux/fs.h> 에 정의되어 있음
• 요청된 작업( **system call** )에 대응할 수 있는 함수들의 포인터를 갖고 있다.
• .owner : device driver 모듈의 host, THIS_MODULE 매크로로 지정 ( linux/module.h )
• .open : deviceFile_open() 로 등록
• .release : deviceFile_release() 로 등록

fops의 동작 방법

deviceFile 에 **특정 API**로 접근하게 되면, **등록된 함수가 호출**된다.
• 특정 API 란 바로 **System call !**
**• open() syscall → .open → deviceFile_open()
• close() syscall → .release → deviceFile_release()**

### 커널이랑 디바이스 드라이버는 어떻게 연결된 겁니까?

`int ret = register_chrdev(NOD_MAJOR, NOD_NAME, &fops);`  //chrdev를 모듈에 등록

커널이 관리하는 chrdev 의 배열에 캐릭터 디바이스 드라이버를 등록하는 API
• unsigned int major : 장치 파일의 major 번호
• const char *name : char 장치 파일 이름
• const struct file_operations *fops : fops

`unregister_chrdev(NOD_MAJOR, NOD_NAME);`

캐릭터 디바이스 드라이버를 해제
• unsigned int major : 장치 파일의 major 번호
• const char *name : char 장치 파일 이름

## 중간 정리

mknod 로 device File 을 직접 만들고,
fops 구조체로 device file로 들어오는 syscall 에 따라 동작 시켰다.
다음 챕터에서는 다른 방법으로 device file 을 만들어 보자.

## 디바이스파일만들기 - 2

디바이스 파일을 만드는 코드가 있다.

mknod 로 /dev/deviceFile 을 생성하면, 재 부팅 할 때마다 매 번 다시 장치 파일을 생성해야 한다.

![image.png](https://prod-files-secure.s3.us-west-2.amazonaws.com/9321cddc-7063-4b63-a848-0ceabf6fe742/ab180d85-dae8-4f8d-a0d7-6a131d38957e/image.png)

## 코드

[**kernel_day1_sample3_devicedriver.c**](https://gist.github.com/hoconoco/17a3012fd4e5d7dd0547932805006b3d#file-kernel_day1_sample3_devicedriver-c)

```c
//mknod 유틸리티 사용하지 않고, device_create(), class_create() 를 사용해 device File 을 생성한 디바이스 드라이버 샘플 코드
//device.h 를 이용해, 장치파일을 생성, 관리한다.
//read용 api 를 추가 생성하여 fops에 등록하여, cat 명령어를 이용해 메시지를 출력한다.

#include <linux/module.h>
#include <linux/printk.h>
#include <linux/init.h>
#include <linux/fs.h>
#include <linux/device.h>   //device file 관리용 header
     
#define NOD_NAME "deviceFile"

MODULE_LICENSE("GPL");

static int NOD_MAJOR;       //device file 의 major num 를 담을 변수
static struct class *cls;   //device file 생성을 위한 class
static dev_t dev;           //device 장치 구분을 위한 번호를 담아줄 변수

static int deviceFile_open(struct inode *inode, struct file *filp){
    pr_info("Open Device\n");
    return 0;
}

static int deviceFile_release(struct inode *inode, struct file *filp){
    pr_info("Close Device\n");
    return 0;
}

static struct file_operations fops = {
    .owner = THIS_MODULE,
    .open = deviceFile_open,
    .release = deviceFile_release,
};

static int __init deviceFile_init(void)
{
    //register_chrdev() 의 첫번째 매개변수는 major num, 0으로 지정하면, 커널이 동적으로 할당한다.
    //return 값이 major num 이다.
    NOD_MAJOR = register_chrdev(0, NOD_NAME, &fops);  
    if( NOD_MAJOR < 0 ){
        pr_alert("Register File\n");
        return NOD_MAJOR;
    }

    pr_info("Insmod Module\n");

    //MKDEV() 를 이용해 장치 구분을 위한 번호 생성 및 할당 
    dev = MKDEV(NOD_MAJOR, 0);
     
    //rpi-6.6 버전 device file를 관리해주는 class 생성
    cls = class_create(NOD_NAME);
     
    //rpi-6.1y 버전 device file를 관리해주는 class 생성
    //cls = class_create(THIS_MODULE, NOD_NAME);
     
    //device file 생성
    device_create(cls, NULL, dev, NULL, NOD_NAME);

    pr_info("Major number %d\n", NOD_MAJOR);
    pr_info("Device file : /dev/%s\n", NOD_NAME);

    return 0;
}

static void __exit deviceFile_exit(void)
{
    //device file 해제
    device_destroy(cls, dev);
    class_destroy(cls);

    unregister_chrdev(NOD_MAJOR, NOD_NAME);
    pr_info("Unload Module\n");
}

module_init(deviceFile_init);
module_exit(deviceFile_exit);
```

[**kernel_day1_sample3_Makefile**](https://gist.github.com/hoconoco/17a3012fd4e5d7dd0547932805006b3d#file-kernel_day1_sample3_makefile)

```makefile
#디바이스 드라이버 

KERNEL_HEADERS=/lib/modules/$(shell uname -r)/build

obj-m += devicedriver.o

PWD := $(CURDIR)

driver:
	make -C $(KERNEL_HEADERS) M=$(PWD) modules

clean:
	make -C $(KERNEL_HEADERS) M=$(PWD) clean
```

이전 코드에서

![image.png](https://prod-files-secure.s3.us-west-2.amazonaws.com/9321cddc-7063-4b63-a848-0ceabf6fe742/2a23310e-6377-43f5-843d-a94700d5104b/image.png)

이 내용이 추가된것

커널에 모듈을 적재하면

→ 장치 파일이 생성되고, Major 번호와 장치 파일 경로를 출력한다.

## 코드 분석

```c
//mknod 유틸리티 사용하지 않고, device_create(), class_create() 를 사용해 device File 을 생성한 디바이스 드라이버 샘플 코드
//device.h 를 이용해, 장치파일을 생성, 관리한다.
//read용 api 를 추가 생성하여 fops에 등록하여, cat 명령어를 이용해 메시지를 출력한다.

#include <linux/module.h>
#include <linux/printk.h>
#include <linux/init.h>
#include <linux/fs.h>
#include <linux/device.h>   //device file 관리용 header
     
#define NOD_NAME "deviceFile"

MODULE_LICENSE("GPL");

static int NOD_MAJOR;       //device file 의 major num 를 담을 변수
static struct class *cls;   //device file 생성을 위한 class
static dev_t dev;           //device 장치 구분을 위한 번호를 담아줄 변수

static int deviceFile_open(struct inode *inode, struct file *filp){
    pr_info("Open Device\n");
    return 0;
}

static int deviceFile_release(struct inode *inode, struct file *filp){
    pr_info("Close Device\n");
    return 0;
}

static struct file_operations fops = {
    .owner = THIS_MODULE,
    .open = deviceFile_open,
    .release = deviceFile_release,
};

static int __init deviceFile_init(void)
{
    //register_chrdev() 의 첫번째 매개변수는 major num, 0으로 지정하면, 커널이 동적으로 할당한다.
    //return 값이 major num 이다.
    NOD_MAJOR = register_chrdev(0, NOD_NAME, &fops);  
    if( NOD_MAJOR < 0 ){
        pr_alert("Register File\n");
        return NOD_MAJOR;
    }

    pr_info("Insmod Module\n");

    //MKDEV() 를 이용해 장치 구분을 위한 번호 생성 및 할당 
    dev = MKDEV(NOD_MAJOR, 0);
     
    //rpi-6.6 버전 device file를 관리해주는 class 생성
    cls = class_create(NOD_NAME);
     
    //rpi-6.1y 버전 device file를 관리해주는 class 생성
    //cls = class_create(THIS_MODULE, NOD_NAME);
     
    //device file 생성
    device_create(cls, NULL, dev, NULL, NOD_NAME);

    pr_info("Major number %d\n", NOD_MAJOR);
    pr_info("Device file : /dev/%s\n", NOD_NAME);

    return 0;
}

static void __exit deviceFile_exit(void)
{
    //device file 해제
    device_destroy(cls, dev);
    class_destroy(cls);

    unregister_chrdev(NOD_MAJOR, NOD_NAME);
    pr_info("Unload Module\n");
}

module_init(deviceFile_init);
module_exit(deviceFile_exit);
```

**`<linux/device.h>`**
• device file 관리용 header
• device_create() / class_create() 등등 device file을 생성 및 관리하는 header 이다.

`static int NOD_MAJOR;       //device file 의 major num 를 담을 변수`
`static struct class *cls;   //device file 생성을 위한 class`
`static dev_t dev;           //device 장치 구분을 위한 번호를 담아줄 변수`

`NOD_MAJOR`
• device file의 major num 을 담을 예정

`class 구조체 변수 생성`
• <linux/device.h> 에 정의됨
• device file 을 관리한다.

`dev 변수`
• dev_t 타입
• 장치 구분을 위한 번호 보관 ( MAJOR )

**Major num을 동적할당 하는 방법**

`NOD_MAJOR = register_chrdev(0, NOD_NAME, &fops);` 

→ 0으로 넣으면 동적으로 할당함 그리고 Major number를 return함

`dev = MKDEV(NOD_MAJOR, 0);`

 주번호와 부번호를 조합해 dev_t 타입으로 return 한다.

`class_create`

 cls = class_create(NOD_NAME);

device file 들을 그룹화하고, 관리하는 class 생성
• name : 생성할 클래스 이름
• return 값 : struct class 포인터 반환

`device_create()`
장치 파일을 생성하는 API
• struct class *class : class 명
• struct device *parent : 부모 장치 이름 , NULL
• dev_t devt : 디바이스 구분을 위한 번호, MKDEV() 의 return 값 ( dev에 저장됨 )으로 생성
• fmt : device file 이름

`device_destroy(struct class *class, dev_t devt)`
• device 파일 삭제
• device file 의 class
• device file 의 주 번호, dev_t 타입

`class_destroy(struct class *class)`
• device file의 class 삭제

# 데이터 송수신

목표

커널 모듈 형식의 디바이스 드라이버를 제어할 App 을 제작한다.
→User space 와 Kernel space 의 관계를 이해하고, system call 을 이용해 data를 송수신한다.

cat 을 이용해서 open / close 하는 대신, 장치 파일에 직접 접근할 수 있는 app 을 제작하자

## 실습

[**kernel_day1_sample3_1_app.c**](https://gist.github.com/hoconoco/c5433de962c3342352cf5b54140dc646#file-kernel_day1_sample3_1_app-c)

```c
//open() , close() syscall을 /dev/deviceFile 로 보내는 app 샘플 코드

#include<stdio.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <stdlib.h>
#include <unistd.h>

#define NOD_NAME "/dev/deviceFile"

int main(){
	int fd = open(NOD_NAME, O_RDWR);
	if( fd<0 ){
		printf("ERROR\n");
		exit(1);
	}
	
	printf("Read DeviceFile!\n");

	close(fd);
		
	return 0;
}
```

[**kernel_day1_sample3_1_devicedriver.c**](https://gist.github.com/hoconoco/c5433de962c3342352cf5b54140dc646#file-kernel_day1_sample3_1_devicedriver-c)

```c
//sample3 코드와 동일, insmod / rmmod 시 deviceFile 생성해주는 커널 모듈 형식의 device driver 샘플코드

#include <linux/module.h>
#include <linux/printk.h>
#include <linux/init.h>
#include <linux/fs.h>
#include <linux/device.h>   //device file 관리용 header
     
#define NOD_NAME "deviceFile"

MODULE_LICENSE("GPL");

static int NOD_MAJOR;       //device file 의 major num 를 담을 변수
static struct class *cls;   //device file 생성을 위한 class
static dev_t dev;

static int deviceFile_open(struct inode *inode, struct file *filp){
    pr_info("Open Device\n");
    return 0;
}

static int deviceFile_release(struct inode *inode, struct file *filp){
    pr_info("Close Device\n");
    return 0;
}

static struct file_operations fops = {
    .owner = THIS_MODULE,
    .open = deviceFile_open,
    .release = deviceFile_release,
};

static int __init deviceFile_init(void)
{
    //register_chrdev() 의 첫번째 매개변수는 major num, 0으로 지정하면, 커널이 동적으로 할당한다.
    //return 값이 major num 이다.
    NOD_MAJOR = register_chrdev(0, NOD_NAME, &fops);  
    if( NOD_MAJOR < 0 ){
        pr_alert("Register File\n");
        return NOD_MAJOR;
    }

    pr_info("Insmod Module\n");

    //device file를 관리해주는 class 생성
    //device file 생성
    dev = MKDEV(NOD_MAJOR, 0);
    cls = class_create(NOD_NAME);
    device_create(cls, NULL, dev, NULL, NOD_NAME);

    pr_info("Major number %d\n", NOD_MAJOR);
    pr_info("Device file : /dev/%s\n", NOD_NAME);

    return 0;
}

static void __exit deviceFile_exit(void)
{
    //device file 해제
    device_destroy(cls, dev);
    class_destroy(cls);

    unregister_chrdev(NOD_MAJOR, NOD_NAME);
    pr_info("Unload Module\n");
}

module_init(deviceFile_init);
module_exit(deviceFile_exit);
```

[**kernel_day1_sample3_1_Makefile**](https://gist.github.com/hoconoco/c5433de962c3342352cf5b54140dc646#file-kernel_day1_sample3_1_makefile)

```c
#app.c도 같이 build 하기 위해 수정
KERNEL_HEADERS=/lib/modules/$(shell uname -r)/build
CC = gcc

TARGET := app
obj-m += devicedriver.o

PWD := $(CURDIR)

#make 시 make all 실행
all: driver app

#driver build
driver:
	make -C $(KERNEL_HEADERS) M=$(PWD) modules

#app build
app:
	$(CC) -o $@ $@.c

#driver, app 모두 제거
clean:
	make -C $(KERNEL_HEADERS) M=$(PWD) clean
	rm -f *.o $(TARGET)
```

**app 을 실행하면, /dev/deviceFile 을 open() / close() 한다.**

- 장치 파일의 권한을 꼭 바꿔야 한다.
- sudo chmod 666 /dev/deviceFile

**한번 더 복습**

User space 와 Kernel space 는 서로 메모리 접근이 안된다!
• 위험 / 금지! → **user space의 메모리 주소와 kernel space의 메모리 주소가 다름**
• app에 생성한 char buf[10]; 의 주소 ( 포인터 )를 kernel로 전송하면, 서로 다른 주소를 가리키게 된다.

![image.png](https://prod-files-secure.s3.us-west-2.amazonaws.com/9321cddc-7063-4b63-a848-0ceabf6fe742/d3b771f7-5e78-450b-b0e2-7346806e9e0d/image.png)

그럼 데이터 어떻게 전송해요??

→copy_to_user() , copy_from_user()

우리가 쓸거 ioctl, copy_to_user(), copy_from_user()

### copy_from/to_user

<linux/uaccess.h> 헤더 필요
• user space → kernel space 로 메시지 전송 : copy_from_user
• kernel space → user space 으로 메시지 전송 : copy_to_user
• 데이터를 받아 복사하는 방식으로 전달

![image.png](https://prod-files-secure.s3.us-west-2.amazonaws.com/9321cddc-7063-4b63-a848-0ceabf6fe742/df36edeb-1302-45d5-b6ad-7c622ae15f53/image.png)

put_user/get_user도 있긴 있는데

`put_user()`
• byte 단위로 데이터를 전송할 때 사용된다.
• byte 단위로 하나 하나 전송해서 더 안전하다.

`copy_to_user()`
• 포인터를 이용해 한번에 전송한다.
• 다량의 큰 데이터 전송 시 유리하다.
• 한번에 넘기므로 크기에 주의한다.

우리는 수업때 copy_to_user, copy_from_user 썼다.

## 실습

copy_to_user, copy_from_user 대신

read + put_user, write + get_user로도 쓸 수 있는데

이거 옛날 자료에서 볼까봐 실습하는거랬지

copy_to_user, copy_from_user 쓰는게 낫다.

[**devicedriver.c**](https://gist.github.com/hoconoco/068f88e1adf6c2a0597127f67eab239f#file-devicedriver-c)

```c
//app으로부터 write() syscall 을 받으면, 넘겨받은 data를 출력하는 device driver 샘플 코드
//app 에서 보낸 read() systeam call 에 data를 전송하는 device driver 샘플 코드

//__user 매크로 : user 메모리 영역을 의미하는 매크로

//fops 의 .write 에 동작시킬 함수를 등록한다.
//fops 구조체의 .read 를 추가해서 함수를 등록한다.

#include <linux/module.h>
#include <linux/printk.h>
#include <linux/init.h>
#include <linux/fs.h>
#include <linux/device.h>  

//get_user(), put_user() 를 위한 헤더
#include <linux/uaccess.h>

#define NOD_NAME "deviceFile"

MODULE_LICENSE("GPL");

static int NOD_MAJOR;		
static struct class *cls;  
static dev_t dev;

//user space에서 받은 데이터 보관용 buffer
static char kernel_buffer[100];

//kernel space 에서 전송할 데이터
static char msg[100] = "HELLO From Kernel!\n";

static int deviceFile_open(struct inode *inode, struct file *filp){
    pr_info("Open Device\n");
    return 0;
}

static int deviceFile_release(struct inode *inode, struct file *filp){
    pr_info("Close Device\n");
    return 0;
}

static ssize_t deviceFile_write(struct file *filp, const char __user *buf, size_t cnt, loff_t *pos ){
	size_t bytes_written = 0;
	
	int i;
	for(i = 0; i<cnt; i++){
		//user space data 복사
		if( get_user(kernel_buffer[i], buf+i) != 0 ){
			return -EFAULT;
		}
	}
	
	pr_info("app msg : %s\n", kernel_buffer);
	bytes_written = cnt;

    return bytes_written;
}

//read() syscall 에 의해 동작하는 함수
//__user 매크로를 사용해서 user 영역의 메모리 공간임을 명시한다.
static ssize_t deviceFile_read(struct file *filp, char __user *buf, size_t cnt, loff_t *pos) {
    int bytes_read = 0;  // 읽은 바이트 수를 저장하는 변수
    
  	const char* msg_ptr = msg;

    // 메시지 버퍼가 비어있으면 0을 반환하여 읽을 데이터가 없음을 나타냅니다.
    if ( !*(msg_ptr + *pos) ){ //메시지 끝
        *pos = 0; //offset 재설정
	 	return 0;	 //파일 끝
	}
  
    //offset 으로 포인터 이동
	msg_ptr += *pos;
    // 요청된 길이 만큼 데이터를 읽고 사용자 공간으로 복사합니다.
    while ( cnt && *msg_ptr ) {
        put_user(*(msg_ptr++), buf++);  // 메시지 버퍼의 데이터를 사용자 버퍼로 복사합니다.
        cnt--;  // 읽은 데이터의 길이를 감소시킵니다.
        bytes_read++;  // 읽은 바이트 수를 증가시킵니다.
    }
	//현재 offset을 새로운 위치로 업데이트 한다.
	*pos += bytes_read;
	
	pr_info("Transfer Data!\n");
    return bytes_read;  // 실제로 읽은 바이트 수를 반환합니다.
}

static struct file_operations fops = {
    .owner = THIS_MODULE,
    .open = deviceFile_open,
    .release = deviceFile_release,
    //.write
	.write = deviceFile_write,
	//.read 
    .read = deviceFile_read,
};

static int __init deviceFile_init(void)
{
    NOD_MAJOR = register_chrdev(0, NOD_NAME, &fops);
    if( NOD_MAJOR < 0 ){
        pr_alert("Register File\n");
        return NOD_MAJOR;
    }

    pr_info("Insmod Module\n");

	dev = MKDEV(NOD_MAJOR, 0);
    cls = class_create(NOD_NAME);
    device_create(cls, NULL, dev, NULL, NOD_NAME);

    pr_info("Major number %d\n", NOD_MAJOR);
    pr_info("Device file : /dev/%s\n", NOD_NAME);

    return 0;
}

static void __exit deviceFile_exit(void)
{
    device_destroy(cls, dev);
    class_destroy(cls);

    unregister_chrdev(NOD_MAJOR, NOD_NAME);
    pr_info("Unload Module\n");
}

module_init(deviceFile_init);
module_exit(deviceFile_exit);
```

[**kernel_day2_read_write_app.c**](https://gist.github.com/hoconoco/068f88e1adf6c2a0597127f67eab239f#file-kernel_day2_read_write_app-c)

```c
//read() / write() system call 로 data를 송수신하는 샘플 코드

#include <stdio.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>

#define NOD_NAME "/dev/deviceFile"

int main(){
	int fd = open(NOD_NAME, O_RDWR);
	if( fd<0 ){
		printf("ERROR\n");
		exit(1);
	}
	
	//kernel space 에서 받은 데이터
	char readbuf[100];
	read(fd, &readbuf, 100);
	printf("read Data : %s\n", readbuf);

	//kernel space 로 보내는 데이터
	char writebuf[100] = "hifaker from User!\n";
	write(fd, &writebuf, strlen(writebuf));
	printf("Transfer Data!\n");

	close(fd);
		
	return 0;
}
```

[**Makefile**](https://gist.github.com/hoconoco/068f88e1adf6c2a0597127f67eab239f#file-makefile)

```makefile
#app.c도 같이 build 하기 위해 수정
KERNEL_HEADERS=/lib/modules/$(shell uname -r)/build
CC = gcc

TARGET := app
obj-m += devicedriver.o

PWD := $(CURDIR)

#make 시 make all 실행
all: driver app

#driver build
driver:
	make -C $(KERNEL_HEADERS) M=$(PWD) modules

#app build
app:
	$(CC) -o $@ $@.c

#driver, app 모두 제거
clean:
	make -C $(KERNEL_HEADERS) M=$(PWD) clean
	rm -f *.o $(TARGET)
```

### 코드 분석

`<linux/uaccess.h>`
• kernel_space 와 user_space 간 데이터 복사를 수행하는 데 사용되는 유틸리티 함수를 제공
• put_user(), copy_to_user(), copy_from_user() 등
• msg
• char 배열
• app으로 전송할 데이터를 보관

`ssize_t read(struct file **filp, char __user *buf, size_t cnt, loff_t***pos)`
• struct file** : 접근 방식, 파일 포인터
• char * : 문자열, **__user 매크로를 이용해서 해당 buf 가 user space의 메모리 영역에 있다는 것을 나타낸다.**
• size_t : 문자열 길이
• loff_t : 파일오프셋 loff_t type,

`ssize_t write(struct file *filp, const char __user *buf, size_t cnt, loff_t *pos)`
• 매개변수는 read 와 동일하다

`long put_user(val, to);`
• 1byte 씩 복사한다.
• val : unsigned long, kernel space 에 있는 데이터
• to : unsigned long __user*, user space 에 데이터를 복사할 주소를 가리키는 포인터
• return : 성공 시 0, 실패 오류
• <arm/uaccess.h> 에 정의

`long get_user(to, from)`
• 1 byte 단위로 데이터를 복사한다.
• to : unsigned long*, kernel space 에 데이터를 복사할 주소
• from : const unsigned long* , user space의 데이터를 가리키는 포인터
• return : 성공 0, 실패 시 오류

## 중간 요약

app이 보낸 system call이 도착하는 지점은? devicefile

devicefile은 device driver와 연결되어있음 → register_chrdev() 로

디바이스드라이버가 동작하기 위해서 fops에 등록해야한다.

우리가 만드는 디바이스드라이버는 캐릭터 디바이스 드라이버다.

→ byte 단위로 데이터를 주고받는다

→ 때문에 read /write로도 가능하지만, 하드웨어 제어와 설정 에서는 ioctl이 훨씬 유리하다!!!

## ioctl

`ioctl ( input output control )`
• <sys/ioctl.h> 필요
• 하드웨어를 제어하기 위한 함수
• 예약된 동작 번호 지정
`int ioctl( int fd, unsigned long request, arg )`
• fd : 파일 디스크립터
**• request : cmd parameter 규칙에 맞춰서 작성**
• arg : 포인터 전달
ex) ioctl(fd, _IO(0,3), 0);

### ioctl을 사용하는 이유

리눅스는 모든 것을 파일로 관리한다.

- 장치에 대응하는 장치 파일을 open() / read() / write() close() 하면 된다?!
- read() / write() 는 실제로 많이 사용하지 않는다.
- ioctl() 을 사용한다.

대부분의 장치는 통신 메커니즘이 필요하다.

- SPI / I2C 등등..

read/write 만으로는 장치와 통신을 할 수 없다.

- 대규모의 데이터 전송도 힘들다.

→ 그래서 ioctl() 을 사용한다

실제 보드를 다뤄보면 우리가 한것처럼 led 같은 단순한 gpio핀을 쓰는게 아니라 통신을 쓴다. → ioctl() 써야한다!!!!

## 실습

[**kernel_day1_sample5_app.c**](https://gist.github.com/hoconoco/df0f142ca8f98f48a622673d23a800cb#file-kernel_day1_sample5_app-c)

```c
#include <stdio.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/ioctl.h> //ioctl 사용을 위한 header

#define NOD_NAME "/dev/deviceFile"

int main(){
    // /dev/deviceFile 을 read/write 로 열기, fops의 .open 실행
    int fd = open(NOD_NAME, O_RDWR);
    if( fd<0 ){
        printf("ERROR\n");
        exit(1);
    }

    //ioctl로 /dev/deviceFile 에 _IO() 매크로로 arg 값 전달
    ioctl(fd, _IO(0,3), 16);        //16 decimal
    ioctl(fd, _IO(0,4), 0xf);       //15 hex
    ioctl(fd, _IO(0,5), 0b1111);    //15 binary
    int ret = ioctl(fd, _IO(0,6), 0);

    //ioctl 의 return 값으로 error 검출
    if(ret < 0){
        printf("%d command invalid!\n", ret);
    }

    close(fd);
    return 0;
}
```

[**kernel_day1_sample5_devicedriver.c**](https://gist.github.com/hoconoco/df0f142ca8f98f48a622673d23a800cb#file-kernel_day1_sample5_devicedriver-c)

```c
#include <linux/module.h>
#include <linux/printk.h>
#include <linux/init.h>
#include <linux/fs.h>
#include <linux/device.h>

#define NOD_NAME "deviceFile"

MODULE_LICENSE("GPL");

static int NOD_MAJOR;
static struct class *cls;
static dev_t dev;

static int deviceFile_open(struct inode *inode, struct file *filp){
    pr_info("Open Device\n");
    return 0;
}

static int deviceFile_release(struct inode *inode, struct file *filp){
    pr_info("Close Device\n");
    return 0;
}

static ssize_t deviceFile_ioctl(struct file *filp, unsigned int cmd, unsigned long arg){
    //입력된 cmd 값 출력
    pr_alert("command number : %d\n", cmd);
    
    //ioctl의 _IO 매크로의 값에 따라 switch문 동작
    switch(cmd){
        case _IO(0,3):
            pr_info("3 - %lu\n", arg);
            break;
        case _IO(0,4):
            pr_info("4 - %lu\n", arg);
            break;
        case _IO(0,5):
            pr_info("5 - %lu\n", arg);
            break;
        default :
            //3~5 이외의 값 입력시, -EINVAL ERROR를 app으로 전송
            return -EINVAL;
    }
    return 0;
}

static struct file_operations fops = {
    .owner = THIS_MODULE,
    .open = deviceFile_open,
    .release = deviceFile_release,
    //ioctl 사용 시 kernel에 lock이 걸리는 현상 방지 ( semaphore )
    .unlocked_ioctl = deviceFile_ioctl,
};

static int __init deviceFile_init(void)
{
    NOD_MAJOR = register_chrdev(NOD_MAJOR, NOD_NAME, &fops);
    if( NOD_MAJOR < 0 ){
        pr_alert("Register File\n");
        return NOD_MAJOR;
    }

    pr_info("Insmod Module\n");
    
    dev = MKDEV(NOD_MAJOR, 0);
    cls = class_create(NOD_NAME);
    device_create(cls, NULL, dev, NULL, NOD_NAME);

    pr_info("Major number %d\n", NOD_MAJOR);
    pr_info("Device file : /dev/%s\n", NOD_NAME);

    return 0;
}

static void __exit deviceFile_exit(void)
{
    device_destroy(cls, dev);
    class_destroy(cls);

    unregister_chrdev(NOD_MAJOR, NOD_NAME);
    pr_info("Unload Module\n");
}

module_init(deviceFile_init);
module_exit(deviceFile_exit);
```

[**kernel_day1_sample5_Makefile**](https://gist.github.com/hoconoco/df0f142ca8f98f48a622673d23a800cb#file-kernel_day1_sample5_makefile)

```makefile
#app.c도 같이 build 하기 위해 수정
KERNEL_HEADERS=/lib/modules/$(shell uname -r)/build
CC = gcc

TARGET := app
obj-m += devicedriver.o

PWD := $(CURDIR)

#make 시 make all 실행
all: driver app

#driver build
driver:
	make -C $(KERNEL_HEADERS) M=$(PWD) modules

#app build
app:
	$(CC) -o $@ $@.c

#driver, app 모두 제거
clean:
	make -C $(KERNEL_HEADERS) M=$(PWD) clean
	rm -f *.o $(TARGET)
```

실행하면

App을 실행하면, ioctl syscall 을 이용해서 kernel 로 data를 전송한다.
• -1 command invalid error 처리

![image.png](https://prod-files-secure.s3.us-west-2.amazonaws.com/9321cddc-7063-4b63-a848-0ceabf6fe742/fc766576-bceb-4deb-956c-64ec623483cd/image.png)

`#include <sys/ioctl.h>`

- ioctl 사용을 위한 헤더
- ioctl() 이용해서 arg 값 전달

 `_IO(type, num)` : cmd parameter 매크로

- arg : 10진수, 2진수, 16진수 전달 가능
- return : device drive에서 처리한 결과 return
API의 return 값은 주로 error 처리에 사용된다.

`arg` : 10진수, 2진수, 16진수 전달 가능

`return` : device drive에서 처리한 결과 return
API의 return 값은 주로 error 처리에 사용된다.

![image.png](https://prod-files-secure.s3.us-west-2.amazonaws.com/9321cddc-7063-4b63-a848-0ceabf6fe742/6c6882e7-2956-4fcc-86bf-faab8ba29e38/image.png)

 

App 에서 보낸 ioctl() syscall에 대응할 API 제작하고

switch 문을 이용하여, cmd 값에 따라 동작한다.
• arg 값을 %lu 로 출력한다. ( unsigned long )
• 그 외 cmd 에 대해서는 error 를 return해서 app 에서 디버깅할 수 있도록 한다

fops 에 등록해서 ioctl() syscall 에 동작하도록 한다.
• .unlocked_ioctl : kernel 이 ioctl 사용 시 lock 이 걸리는 데, 이를 방지하도록 한다.

cmd parameter 를 일일이 지켜가며 개발하는 것은 매우 많은 시간이
걸린다.
→ 그래서 매크로가 제공된다.
• `_IO(type, number)` : 단순한 타입 ← 우리 수업에서 사용하는 매크로
• `_IOR(type, number :` 전송 받을 데이터 타입) : read용
• `_IOW(type, number`, 전송 보낼 데이터 타입) : write용
• `_IOWR(type, number`, 전송 주고 받을 데이터 타입) : 둘다
_IO(0,1) / _IO(0,2) 는 시스템에서 사용하고 있기 때문에,
_IO(0,3) 부터 사용한다.

h/w 개발을 할 때, API를 쓸 때마다, error의 위험이 있다.

h/w 는 보통 메모리를 직접 건드릴 가능성이 매우 높기 때문에 error의 위험성이 상당히 크게 다가온다. → 따라서 개발자는 error 가 날 수 있을 모든 곳에 error 검출을 위한 코드를 작성한다.

## 하지만 이렇게 값만 넘기는게 무슨 의미가 있는가?? 상태에 따라 값이 바뀌어야 한다. → 변수, 구조체 활용하여 데이터 주거니 받거니

### ioctl + copy_to_user

[**kernel_day1_sample6_1_app.c**](https://gist.github.com/hoconoco/6c9cfec40d911a6e224a091ab71abbad#file-kernel_day1_sample6_1_app-c)

```c
#include <stdio.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/ioctl.h>

#define NOD_NAME "/dev/deviceFile"

char buf[30];
int main(){
    int fd = open(NOD_NAME, O_RDWR);
    if( fd<0 ){
        printf("ERROR\n");
        exit(1);
    }

    ioctl(fd, _IO(0,3), buf);
    printf("kernel Data : %s\n", buf);

    close(fd);
    return 0;
}
```

[**kernel_day1_sample6_1_devicedriver.c**](https://gist.github.com/hoconoco/6c9cfec40d911a6e224a091ab71abbad#file-kernel_day1_sample6_1_devicedriver-c)

```c
#include <linux/module.h>
#include <linux/printk.h>
#include <linux/init.h>
#include <linux/fs.h>
#include <linux/device.h>
#include <linux/uaccess.h>

#define NOD_NAME "deviceFile"

MODULE_LICENSE("GPL");

static int NOD_MAJOR;
static struct class *cls;
static dev_t dev;

static int deviceFile_open(struct inode *inode, struct file *filp){
    pr_info("Open Device\n");
    return 0;
}

static int deviceFile_release(struct inode *inode, struct file *filp){
    pr_info("Close Device\n");
    return 0;
}

static ssize_t deviceFile_ioctl(struct file *filp, unsigned int cmd, unsigned long arg){
    pr_alert("command number : %d\n", cmd);
   	
    char buf[30] = "THIS IS KERNEL DATA!";
    int ret; 
    switch(cmd){
        case _IO(0,3):
            ret = copy_to_user((void*)arg, (void*)buf, sizeof(buf));
	    pr_info("Trasfer Data!\n");
            break;
    }
    return 0;
}

static struct file_operations fops = {
    .owner = THIS_MODULE,
    .open = deviceFile_open,
    .release = deviceFile_release,
    //ioctl 사용 시 kernel에 lock이 걸리는 현상 방지 ( semaphore )
    .unlocked_ioctl = deviceFile_ioctl,
};

static int __init deviceFile_init(void)
{
    NOD_MAJOR = register_chrdev(NOD_MAJOR, NOD_NAME, &fops);
    if( NOD_MAJOR < 0 ){
        pr_alert("Register File\n");
        return NOD_MAJOR;
    }

    pr_info("Insmod Module\n");
	
    dev = MKDEV(NOD_MAJOR, 0);
    cls = class_create(NOD_NAME);
    device_create(cls, NULL, dev, NULL, NOD_NAME);

    pr_info("Major number %d\n", NOD_MAJOR);
    pr_info("Device file : /dev/%s\n", NOD_NAME);

    return 0;
}

static void __exit deviceFile_exit(void)
{
    device_destroy(cls, dev);
    class_destroy(cls);

    unregister_chrdev(NOD_MAJOR, NOD_NAME);
    pr_info("Unload Module\n");
}

module_init(deviceFile_init);
module_exit(deviceFile_exit);
```

[**kernel_day1_sample6_1_Makefile**](https://gist.github.com/hoconoco/6c9cfec40d911a6e224a091ab71abbad#file-kernel_day1_sample6_1_makefile)

```c
#app.c도 같이 build 하기 위해 수정
KERNEL_HEADERS=/lib/modules/$(shell uname -r)/build
CC = gcc

TARGET := app
obj-m += devicedriver.o

PWD := $(CURDIR)

#make 시 make all 실행
all: driver app

#driver build
driver:
	make -C $(KERNEL_HEADERS) M=$(PWD) modules

#app build
app:
	$(CC) -o $@ $@.c

#driver, app 모두 제거
clean:
	make -C $(KERNEL_HEADERS) M=$(PWD) clean
	rm -f *.o $(TARGET)
@YunJiUk
Comment

```

코드 분석

`copy_to_user(void __user *to, const void *from, unsigned long n)`
• arg 의 포인터
• kernel 에 있는 data 포인터
• 길이
`<linux/uaccess.h>` 필요
user space 로 data 를 보낼 때 사용한다.

![image.png](https://prod-files-secure.s3.us-west-2.amazonaws.com/9321cddc-7063-4b63-a848-0ceabf6fe742/8f2d8f68-a59b-4f67-bf7e-1c0dba6a95ec/image.png)

### 다음은 copy_from_user

[**kernel_day1_sample6_app.c**](https://gist.github.com/hoconoco/56370e3418bd9c8c3cfac5a6bd579813#file-kernel_day1_sample6_app-c)

```python
//ioctl 로 kernel space 로 data 전송하는 app 샘플코드

#include <stdio.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/ioctl.h>

#define NOD_NAME "/dev/deviceFile"

char buf[30] = "THIS IS APP DATA!";
int main(){
    int fd = open(NOD_NAME, O_RDWR);
    if( fd<0 ){
        printf("ERROR\n");
        exit(1);
    }

    ioctl(fd, _IO(0,3), buf);
    printf("Transfer Data!\n");

    close(fd);
    return 0;
}
```

[**kernel_day1_sample6_devicedriver.c**](https://gist.github.com/hoconoco/56370e3418bd9c8c3cfac5a6bd579813#file-kernel_day1_sample6_devicedriver-c)

```python
//copy_from_user API 를 사용해서 app으로부터 data를 받아오는 devicedriver 샘플코드
//<linux/uaccess.h> 사용
//void* 를 이용해 data를 가져온다.

#include <linux/module.h>
#include <linux/printk.h>
#include <linux/init.h>
#include <linux/fs.h>
#include <linux/device.h>
#include <linux/uaccess.h>

#define NOD_NAME "deviceFile"

MODULE_LICENSE("GPL");

static int NOD_MAJOR;
static struct class *cls;
static dev_t dev;

static int deviceFile_open(struct inode *inode, struct file *filp){
    pr_info("Open Device\n");
    return 0;
}

static int deviceFile_release(struct inode *inode, struct file *filp){
    pr_info("Close Device\n");
    return 0;
}

static ssize_t deviceFile_ioctl(struct file *filp, unsigned int cmd, unsigned long arg){
    pr_alert("command number : %d\n", cmd);	
    char buf[30];
    int ret; 
    switch(cmd){
        case _IO(0,3):
            ret = copy_from_user((void*)buf, (void*)arg, sizeof(buf));
	    pr_info("app data : %s\n", buf);
            break;
    }
    return 0;
}

static struct file_operations fops = {
    .owner = THIS_MODULE,
    .open = deviceFile_open,
    .release = deviceFile_release,
    .unlocked_ioctl = deviceFile_ioctl,
};

static int __init deviceFile_init(void)
{
    NOD_MAJOR = register_chrdev(NOD_MAJOR, NOD_NAME, &fops);
    if( NOD_MAJOR < 0 ){
        pr_alert("Register File\n");
        return NOD_MAJOR;
    }

    pr_info("Insmod Module\n");
	
    dev = MKDEV(NOD_MAJOR, 0);
    cls = class_create(NOD_NAME);
    device_create(cls, NULL, dev, NULL, NOD_NAME);

    pr_info("Major number %d\n", NOD_MAJOR);
    pr_info("Device file : /dev/%s\n", NOD_NAME);

    return 0;
}

static void __exit deviceFile_exit(void)
{
    device_destroy(cls, dev);
    class_destroy(cls);

    unregister_chrdev(NOD_MAJOR, NOD_NAME);
    pr_info("Unload Module\n");
}

module_init(deviceFile_init);
module_exit(deviceFile_exit);
```

[**kernel_day1_sample6_Makefile**](https://gist.github.com/hoconoco/56370e3418bd9c8c3cfac5a6bd579813#file-kernel_day1_sample6_makefile)

```python
#app.c도 같이 build 하기 위해 수정
KERNEL_HEADERS=/lib/modules/$(shell uname -r)/build
CC = gcc

TARGET := app
obj-m += devicedriver.o

PWD := $(CURDIR)

#make 시 make all 실행
all: driver app

#driver build
driver:
	make -C $(KERNEL_HEADERS) M=$(PWD) modules

#app build
app:
	$(CC) -o $@ $@.c

#driver, app 모두 제거
clean:
	make -C $(KERNEL_HEADERS) M=$(PWD) clean
	rm -f *.o $(TARGET)
```

`copy_from_user(void* to, const void __user *from, unsigned long n)`
• kernel space에 저장할 data 포인터 ( void* 로 쉽게 저장 )
• user space로 부터 받아온 data 포인터
• 길이
<linux/uaccess.h> 필요
user space 에서 넘어온 data 를 kernel 에서 받을 때 사용한다.