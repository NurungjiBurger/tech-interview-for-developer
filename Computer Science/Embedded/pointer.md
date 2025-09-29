# 포인터

- 메모리 주소를 보관하는 변수
- 기계어나 어셈블리 언어처럼 메모리 주소를 갖고 직접 메모리 내용에 접근해서 조작
- 동적 메모리 할당(malloc) , linked list 등 향상된 자료구조에도 사용

![image.png](https://prod-files-secure.s3.us-west-2.amazonaws.com/9321cddc-7063-4b63-a848-0ceabf6fe742/2b722724-6e6c-4229-b74b-fca4fa413bbc/image.png)

### 왜 사용할까?

- 데이터 복사를 피하고 데이터를 공유하여 작업하고자 할 때
    - 즉 메모리의 추가 사용 방지
- 메모리에 직접 접근하는 경우가 필요할 경우에도 반드시 필요
    - 임베디드 프로그래밍 할 때
        - 하드웨어를 제어하는 소프트웨어를 만드는

```cpp
int x = 10;    // 변수 x는 값 10을 가짐
int *p = &x;   // p는 x의 주소를 가리킴
int **pp = &p; // pp는 p의 주소를 가리킴

int rows = 3, cols = 4;
int **array = (int **)malloc(rows * sizeof(int *));
for (int i = 0; i < rows; i++) {
    array[i] = (int *)malloc(cols * sizeof(int));
}
```

### 연습문제(각자 풀어보세요)

## int a[8] = {1,2,3,4,5,6,7,8} a의 주소는 0x1000

a+1 

*a+1 

*(a+2)
&a[3]

## int b[3][4]={ {1,2,3,4} , {5,6,7,8} , {9,10,11,12} } b = 0x2000

b+1 
*(b+1) 
* ( * (b+2) + 3 ) 

&b[1][0] == b[1] + 1

### 메모리 영역

char* v = “ABCD”

- 이거는?
    
    왜냐 “ABCD”는 문자열 상수기 때문에 이제 텍스트 세그먼트라는 곳으로 감
    
    const를 선언해줘야 할 수 있다
    

char[] 는?

char의 배열임 즉 char는 값을 변경할 수 있는 stack 영역에 저장

![image.png](https://prod-files-secure.s3.us-west-2.amazonaws.com/9321cddc-7063-4b63-a848-0ceabf6fe742/bb2645d5-ff3b-4c75-a94e-4a282a9e0d24/image.png)

- stack  지역 변수 함수 (컴파일시 크기 결정)
- heap 동적 메모리 할당을 위한 영역(malloc)
- BSS (초기화 되지 않은 전역변수와 정적 변수) (static)
- Data (초기화 된 전역 변수와 정적 변수)
- code (프로그램의 실행 코드)

### 배열 포인터와 포인터 배열 (보면 딱 뭔지 느낌이 와야함)

int* p[3] = {&a,&b,&c}

int arr[3] = {10,20,30}

int(*p)[3] = arr;

### 함수 포인터

void abd(int a){

}

int main(){

void (*p)(int);

p = abd;

abd(10);

```cpp
void abd (int a);

int(*p)(int)
```

}

### 함수 포인터배열

int abc(int n){}

int (*p[2])(int) = {abc,bbq};

![image.png](https://prod-files-secure.s3.us-west-2.amazonaws.com/9321cddc-7063-4b63-a848-0ceabf6fe742/2ba9bdfb-f4bf-48f7-b01c-cc9ba2caca39/image.png)