import cv2 #pip install opencv-python
import numpy as np #pip install numpy

def image_transform(img_input):
        img_input = cv2.cvtColor(img_input, cv2.COLOR_RGB2GRAY)
        img_input = cv2.GaussianBlur(img_input, (5, 5), 0)
        img_input = cv2.Canny(img_input, 100, 160)
        return img_input

def contours_search(img):
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
        closed = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
        con = cv2.findContours(closed.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
        return con

def image_scanning(img_input, con):
        global relation

        def isequal_perimeter(a, b):
                if (max((a - b), (b - a)) > min(a, b) * 0.05): return False
                else: return True

        def isequal_colour(a, b):
                if ((max((a[0] - b[0]), (b[0] - a[0])) < 50) and (max((a[1] - b[1]), (b[1] - a[1])) < 50) and (max((a[2] - b[2]), (b[2] - a[2])) < 50)):
                        return True
                else: return False

        def find_color(input, pixel):
                pixel = pixel.tolist()
                env_pixel = [[pixel[0], pixel[1] + 2], [pixel[0] + 2, pixel[1]], [pixel[0] - 2, pixel[1]], [pixel[0], pixel[1] - 2]]
                for pix in env_pixel:
                        c = input[pix[1]][pix[0]].tolist()
                        if not isequal_colour(c, [255, 253, 252]): return c
                        else: return 'error'
        
        def find(sorted, cont):
                for i in range(len(sorted)):
                        if (sorted[i][0][0].tolist()[0] == cont[0][0].tolist()[0]) and (sorted[i][0][0].tolist()[1] == cont[0][0].tolist()[1]):
                                return i

        
        perimeters = []
        colors = []
        elem_array = []
        

        sorted_rows = sorted(con, key=lambda x: int(x[0][0].tolist()[0]))
        sorted_cols = sorted(con, key=lambda x: int(x[0][0].tolist()[1]))

        q = 0
        for cont in con:
                perimeter = cv2.arcLength(cont, True)
                if len(perimeters) != 0:
                        f = True
                        for p in perimeters:
                                if isequal_perimeter(p, perimeter): perimeter = p; f = False
                        if f: perimeters.append(perimeter)
                else: perimeters.append(perimeter)
                
                color = find_color(img_input, cont[0][0])
                if len(colors) != 0:
                        f = True
                        for colr in colors:
                                if isequal_colour(color, colr): color = colr; f = False
                        if f: colors.append(color)
                else: colors.append(color)
                row = find(sorted_rows, cont) // int(len(con) ** 0.5)
                col = find(sorted_cols, cont) // int(len(con) ** 0.5)
                id = row + col * int(len(con) ** 0.5)
                relation[q] = id
                elem_array.append([perimeter, color, col, row, id])
                q += 1

        return elem_array

def get_final_elem_array(elem_array):
        
        class elem:
                shape_type = None
                color_type = None
                row = None
                col = None
                id = None
                def __init__(self, shape_type, color_type, col, row, id) -> None:
                        self.shape_type = shape_type
                        self.color_type = color_type
                        self.row = row
                        self.col = col
                        self.id = id
                
                def getcolor(self): return self.color_type
                def getshape(self): return self.shape_type
                def getrow(self): return self.row
                def getcol(self): return self.col
                def getid(self): return self.id

        final_elem_array = []
        shape_list = []
        color_list = []
        for item in elem_array:
                if item[0] not in shape_list: shape_list.append(item[0])
                if item[1] not in color_list: color_list.append(item[1])
                for i in range(len(shape_list)):
                        if shape_list[i] == item[0]: shape_type = i
                for i in range(len(color_list)):
                        if color_list[i] == item[1]: color_type = i
                final_elem_array.append(elem(shape_type, color_type, item[2], item[3], item[4]))
        return final_elem_array

def tomatrix(final_elem_array):
        matrix = []
        col_id = 0
        for item in final_elem_array:
                matrix.append([])
                for other_item in final_elem_array:
                        if item == other_item: matrix[col_id].append(0)
                        else: 
                                if ((item.getcol() == other_item.getcol()) or (item.getrow() == other_item.getrow())):
                                        if ((item.getshape() == other_item.getshape()) or (item.getcolor() == other_item.getcolor())):
                                                matrix[col_id].append(1)
                                        else: matrix[col_id].append(0)
                                else: matrix[col_id].append(0)
                col_id += 1
        return matrix

def matrix_to_graph(matrix):
    graph = {}
    for i, node in enumerate(matrix):
        adj = []
        for j, connected in enumerate(node):
            if connected:
                adj.append(j)
        graph[i] = adj
    return graph

def work_img_create(img, con, final_elem_array):
        color_ex = [(0, 255, 255), (0, 204, 0), (255, 0 ,0), (127, 0 ,255), (0, 128, 255)]
        q = 0
        for cont in con:
                sm = cv2.arcLength(cont, True)
                apd = cv2.approxPolyDP(cont, 0.0001*sm, True)
                # visual contours 
                # cv2.drawContours(img, [apd], -1, (254, 19, 186), 4)
                # visual columns and rows  
                # cv2.putText(img, f'{final_elem_array[q].getcol()}:{final_elem_array[q].getrow()}', apd[0][0], cv2.FONT_HERSHEY_TRIPLEX, 1, (254, 19, 186), 1)
                # visual id
                cv2.putText(img, f'{final_elem_array[q].getid()}', apd[0][0], cv2.FONT_HERSHEY_TRIPLEX, 1, (254, 19, 186), 1)
                q += 1
        return img

def draw_way(work_img, way):
        box = []
        color_ex = [(0, 255, 255), (0, 204, 0), (255, 0 ,0), (127, 0 ,255), (0, 128, 255), (92, 92, 205), (130, 0, 75)]

        for i in con:
                box.append(i[0][0].tolist())

        for i in range(len(way) - 1):
                cv2.line(work_img, box[way[i]], box[way[i + 1]], color_ex[i % len(color_ex)], thickness=2)

def way_search(graph, con):
        def hui(graph, id, top, marks = [False] * len(con)):
                top.append(id)
                marks[id] = True
                for i in graph[id]:
                        if(not marks[i]):
                                t = hui(graph, i, top, marks)
                                if len(t) < len(marks) :
                                        marks[i] = False
                                        t.pop()
                                else : 
                                        return t
                return top
        
        for id in graph:
                top = []
                top = hui(graph, id, top)
                if len(top) == len(con): return top

if __name__ == '__main__':
        relation = {}
        # way to image
        path = "images/7sizeinput.jpg"
        img_input = cv2.imread(path)
        img = image_transform(img_input)
        con = contours_search(img)
        final_elem_array = get_final_elem_array(image_scanning(img_input, con))
        matrix = tomatrix(final_elem_array)
        graph = matrix_to_graph(matrix)
        work_img = work_img_create(img_input, con, final_elem_array)
        
        way_q = way_search(graph, con)
        way_id = []
        for q in way_q:
                way_id.append(relation[q])
        print(way_id)
        
        # draw_way() # trial version: ugly
        cv2.imshow('result.jpg', work_img)
        cv2.waitKey(0)