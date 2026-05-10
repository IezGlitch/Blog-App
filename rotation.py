def rotate_left(arr):
    n=len(arr)
    for i in range(3):
        temp=arr[0]
        for j in range(0,n-1):
            arr[j]=arr[j+1]
        arr[j]=temp
    return arr
def rotate_right(arr):
    n=len(arr)
    for i in range(3):
        temp=arr[n-1]
        for j in range(n-1,0,-1):
            arr[j]=arr[j-1]
        arr[0]=temp
    return arr
data=input("enter elements of array separated by space")
l=[x for x in data.split()]
s=input("entechoice L/R")
if(s.upper()=="L"):
    print(rotate_left(l))
elif(s.upper()== "R") :
    print(rotate_right(l))
else:
    print("enter valid choice")
