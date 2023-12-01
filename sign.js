let CryptoJS = require("crypto-js");

function sha1_hash(word) {
    return CryptoJS.SHA1(word).toString(CryptoJS.enc.Hex);
}
function md5_hash(word) {
    return CryptoJS.MD5(word).toString(CryptoJS.enc.Hex);
}

function generateRandomString(length) {
    let result = '';
    const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    const charactersLength = characters.length;
    for (let i = 0; i < length; i++) {
      result += characters.charAt(Math.floor(Math.random() * charactersLength));
    }
    return result;
}

function get_did() {
    return md5_hash(generateRandomString(16));
}

function get_sign_text(input) {
    let output = []
    let ptr = input;
    let output_index = 4;
    while (input.length >> 1 > output_index - 4) {
        const c1 = ptr.charCodeAt(0);
        const c2 = ptr.charCodeAt(1);
        const byte = ((c1 & 0xF0) | (c2 & 0xF));
        output[output_index++] = byte;
        ptr = ptr.slice(2);
    }
    return output.map(value => {
        return String.fromCharCode(value)
    }).join('')
}

function deal_array(params) {
    let result = [];
    for (let i = 0; i < params.length; i++) {
        value = params[i];
        if (["{}", "[]", ""].indexOf(value.toString()) != -1) {
            value = "";
        }
        if (Array.isArray(value)) {
            value = deal_array(value);
        } else if (typeof value == "object") {
            value = deal_dict(value);
        }
        result.push(`${i}=${value}`);
    }
    return result.join("&");
}

function deal_dict(params) {
    let result = [],
        value;
    for (let key of Object.keys(params).sort()) {
        value = params[key];
        if (["{}", "[]", ""].indexOf(value.toString()) != -1) {
            value = "";
        }
        if (Array.isArray(value)) {
            value = deal_array(value);
        } else if (typeof value == "object") {
            value = deal_dict(value);
        }
        result.push(`${key}=${value}`);
    }
    return result.join("&");
}

function nice_sign_v3(JsonData, did, random) {
    let result = {
        data: "",
        random: random || generateRandomString(16),
        did: did || get_did()
    }
    let md5_list = [];
    md5_list.push(md5_hash(result.did.substring(16, 32) + result.did.substring(0, 16)));
    md5_list.push(md5_hash(result.random + md5_list[0] + "8a5f746c1c9c99c0b458e1ed510845e5"));
    md5_list[1] = md5_list[1].substring(16, 32) + md5_list[1].substring(0, 16)
    let obj = JsonData === "" ? {} : typeof JsonData === "string" ? JSON.parse(JsonData) : JsonData
    let input = deal_dict(obj);
    let sign_text = get_sign_text(input);
    let sign = sha1_hash(sign_text + md5_list[1])
    result.data = `nice-sign-v1://${sign.substring(24, 41) + sign.substring(8, 24)}:${result.random}/${JSON.stringify(obj)}`
    return JSON.stringify(result)
}

