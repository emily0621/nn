import {Component, OnInit, Renderer2} from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit{

  predict_on_test_dataset = true;
  read_text_from_dataset = false;
  write_and_read = false;

  is_data_loaded = false;

  title = 'frontend';
  image = '';
  predicted_label = '';
  label = '';

  form_images = [];
  form_text = '';

  constructor(private renderer: Renderer2, private http: HttpClient) { }

  predict(): void {
    this.is_data_loaded = false;
    this.http.get('http://127.0.0.1:5000/predict').subscribe((response:any) => {
      this.image = 'data:image/png;base64,' + response['image'];
      this.predicted_label = response['predicted_label'];
      this.label = response['label'];
      this.is_data_loaded = true;
    });
  }


  predict_form() {
    this.is_data_loaded = false;
    this.http.get('http://127.0.0.1:5000/random_form').subscribe((response:any) => {
      this.form_images = response['images'];
      this.form_text = response['text']
      this.is_data_loaded = true;
    });
  }

  ngOnInit(): void {
    this.predict()
  }

  predict_on_test_dataset_function() {
    this.predict()
    this.read_text_from_dataset = false;
    this.write_and_read = false;
    this.predict_on_test_dataset = true;
  }

  read_text_from_dataset_function() {
    this.predict_form()
    this.predict_on_test_dataset = false;
    this.write_and_read = false;
    this.read_text_from_dataset = true;
  }

  write_and_read_function() {
    this.read_text_from_dataset = false;
    this.predict_on_test_dataset = false;
    this.write_and_read = true;
  }
}
