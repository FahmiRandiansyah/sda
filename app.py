import os
import json
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
DATA_FILE = "inventori.json"

class Node:
    def __init__(self, id_barang, nama, kategori, stok, harga):
        self.id = id_barang
        self.nama = nama
        self.kategori = kategori
        self.stok = int(stok)
        self.harga = float(harga)
        self.height = 1
        self.left = None
        self.right = None

    def to_dict(self):
        return {
            "id": self.id,
            "nama": self.nama,
            "kategori": self.kategori,
            "stok": self.stok,
            "harga": self.harga
        }

class AVLTree:
    def __init__(self):
        self.root = None

    def get_height(self, node):
        if not node:
            return 0
        return node.height

    def get_balance(self, node):
        if not node:
            return 0
        return self.get_height(node.left) - self.get_height(node.right)

    def right_rotate(self, y):
        x = y.left
        T2 = x.right
        x.right = y
        y.left = T2
        y.height = 1 + max(self.get_height(y.left), self.get_height(y.right))
        x.height = 1 + max(self.get_height(x.left), self.get_height(x.right))
        return x

    def left_rotate(self, x):
        y = x.right
        T2 = y.left
        y.left = x
        x.right = T2
        x.height = 1 + max(self.get_height(x.left), self.get_height(x.right))
        y.height = 1 + max(self.get_height(y.left), self.get_height(y.right))
        return y

    def insert(self, root, node):
        if not root:
            return node
        if node.id < root.id:
            root.left = self.insert(root.left, node)
        elif node.id > root.id:
            root.right = self.insert(root.right, node)
        else:
            return root

        root.height = 1 + max(self.get_height(root.left), self.get_height(root.right))
        balance = self.get_balance(root)

        # Case 1 - Left Left
        if balance > 1 and node.id < root.left.id:
            return self.right_rotate(root)
        # Case 2 - Right Right
        if balance < -1 and node.id > root.right.id:
            return self.left_rotate(root)
        # Case 3 - Left Right
        if balance > 1 and node.id > root.left.id:
            root.left = self.left_rotate(root.left)
            return self.right_rotate(root)
        # Case 4 - Right Left
        if balance < -1 and node.id < root.right.id:
            root.right = self.right_rotate(root.right)
            return self.left_rotate(root)

        return root

    def get_min_value_node(self, root):
        if root is None or root.left is None:
            return root
        return self.get_min_value_node(root.left)

    def delete(self, root, id_barang):
        if not root:
            return root
        if id_barang < root.id:
            root.left = self.delete(root.left, id_barang)
        elif id_barang > root.id:
            root.right = self.delete(root.right, id_barang)
        else:
            # Node dengan satu anak atau tanpa anak
            if root.left is None:
                temp = root.right
                root = None
                return temp
            elif root.right is None:
                temp = root.left
                root = None
                return temp
            
            # Node dengan dua anak
            temp = self.get_min_value_node(root.right)
            
            # AMAN: Mengamankan ID suksesor ke dalam variabel sementara sebelum root ditimpa
            target_id = temp.id
            
            # Salin data suksesor ke root
            root.id = temp.id
            root.nama = temp.nama
            root.kategori = temp.kategori
            root.stok = temp.stok
            root.harga = temp.harga
            
            # Hapus node suksesor menggunakan target_id yang aman
            root.right = self.delete(root.right, target_id)

        if root is None:
            return root

        root.height = 1 + max(self.get_height(root.left), self.get_height(root.right))
        balance = self.get_balance(root)

        # Case 1 - Left Left
        if balance > 1 and self.get_balance(root.left) >= 0:
            return self.right_rotate(root)
        # Case 2 - Left Right
        if balance > 1 and self.get_balance(root.left) < 0:
            root.left = self.left_rotate(root.left)
            return self.right_rotate(root)
        # Case 3 - Right Right
        if balance < -1 and self.get_balance(root.right) <= 0:
            return self.left_rotate(root)
        # Case 4 - Right Left
        if balance < -1 and self.get_balance(root.right) > 0:
            root.right = self.right_rotate(root.right)
            return self.left_rotate(root)

        return root

    def search(self, root, id_barang):
        if not root or root.id == id_barang:
            return root
        if id_barang < root.id:
            return self.search(root.left, id_barang)
        return self.search(root.right, id_barang)

    def inorder_list(self, root, res):
        if root:
            self.inorder_list(root.left, res)
            res.append(root.to_dict())
            self.inorder_list(root.right, res)

# Inisialisasi Pohon AVL Global
tree = AVLTree()

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                items = json.load(f)
                for item in items:
                    node = Node(item['id'], item['nama'], item['kategori'], item['stok'], item['harga'])
                    tree.root = tree.insert(tree.root, node)
        except Exception as e:
            print("Gagal memuat berkas JSON:", e)

def save_data():
    res = []
    tree.inorder_list(tree.root, res)
    with open(DATA_FILE, 'w') as f:
        json.dump(res, f, indent=4)

# Algoritma Pengurutan (Merge Sort) untuk Laporan Kustom
def merge_sort(arr, key, reverse=False):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid], key, reverse)
    right = merge_sort(arr[mid:], key, reverse)
    return merge(left, right, key, reverse)

def merge(left, right, key, reverse):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        condition = (left[i][key] > right[j][key]) if reverse else (left[i][key] < right[j][key])
        if condition:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result

# Muat data awal saat server menyala
load_data()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/barang', methods=['GET'])
def get_all_barang():
    res = []
    tree.inorder_list(tree.root, res)
    sort_by = request.args.get('sort_by', None)
    if sort_by in ['stok', 'harga']:
        res = merge_sort(res, sort_by)
    return jsonify(res)

@app.route('/api/barang', methods=['POST'])
def add_barang():
    data = request.json
    id_barang = data.get('id', '').strip()
    nama = data.get('nama', '').strip()
    kategori = data.get('kategori', '').strip()
    stok = data.get('stok', 0)
    harga = data.get('harga', 0)

    if not id_barang or not nama:
        return jsonify({"success": False, "message": "ID dan Nama barang wajib diisi!"}), 400

    is_exist = tree.search(tree.root, id_barang)
    if is_exist:
        return jsonify({
            "success": False, 
            "message": f"ID Barang '{id_barang}' sudah terdaftar dengan nama '{is_exist.nama}'. Harap gunakan ID unik lain!"
        }), 400

    node = Node(id_barang, nama, kategori, stok, harga)
    tree.root = tree.insert(tree.root, node)
    save_data()
    return jsonify({"success": True, "message": f"Barang {nama} berhasil disimpan ke AVL Tree."})

# --- ROUTE UPDATE BARANG (PUT) ---
@app.route('/api/barang/<id_barang>', methods=['PUT'])
def update_barang(id_barang):
    data = request.json
    nama = data.get('nama', '').strip()
    kategori = data.get('kategori', '').strip()
    stok = data.get('stok', 0)
    harga = data.get('harga', 0)

    if not nama:
        return jsonify({"success": False, "message": "Nama barang wajib diisi!"}), 400

    # Cari node barang lama di dalam AVL Tree
    target_node = tree.search(tree.root, id_barang)
    if not target_node:
        return jsonify({"success": False, "message": "Barang tidak ditemukan!"}), 404

    # Perbarui atribut data (Struktur / Kunci ID AVL tidak berubah)
    target_node.nama = nama
    target_node.kategori = kategori
    target_node.stok = int(stok)
    target_node.harga = float(harga)
    
    save_data()
    return jsonify({"success": True, "message": f"Barang dengan ID {id_barang} berhasil diperbarui!"})

@app.route('/api/barang/<id_barang>', methods=['DELETE'])
def delete_barang(id_barang):
    found = tree.search(tree.root, id_barang)
    if not found:
        return jsonify({"success": False, "message": "Barang tidak ditemukan!"}), 404
    
    tree.root = tree.delete(tree.root, id_barang)
    save_data()
    return jsonify({"success": True, "message": "Barang berhasil dihapus dari AVL Tree."})

@app.route('/api/barang/cari/<id_barang>', methods=['GET'])
def search_barang(id_barang):
    found = tree.search(tree.root, id_barang)
    if found:
        return jsonify({"success": True, "data": found.to_dict()})
    return jsonify({"success": False, "message": "Barang tidak ditemukan!"}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)