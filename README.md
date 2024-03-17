# YATLA 📑: Yet Another Templating Language (Again!)

YATLA is a templating engine with a simple templating language specifically designed for type inference, allowing consumers to provide users with slots of determined types.

## Roadmap 🗺️

- [x] Add numerical blocks
- [x] Add type inference. Go from a template -> list of typed parameters
- [x] Write own lexer to respect whitespace
- [x] Write own own parsing system
- [x] Add template validation (preventing non-unique identifiers...)
- [x] Publish as pip-installable package
- [x] Add foreach loops
- [x] Add numerical function calls
- [ ] Improve Python interface
- [ ] Think about object accessors

## Sample Template

This sample template gives a whirlwind tour of YATLA's functionality.

```
This a sample template.

This line contains a {{ slot }}.

Slots can also contain mathematical expressions: {{ 3 + factor * 7 }}.
With full support for operator precedence: {{ (3 + factor) * 7 }}.

Foreach loops are also valid. For example:

This is the {{ factor }} times table:
{{ foreach num in num_list }}
    {{ factor }} * {{ num }} = {{ factor * num }}
{{ endforeach }}

There is also a standard library of mathematical functions.
Comparing {{ factor }} and {{ num }}, the largest is {{ Maximum(factor, num) }} and the smallest is {{ Minimum(factor, num) }}.
{{ RoundUp(15, 2) }} = 16, and {{ RoundDown(15, 2) }} = 14. 
```

From the template above, YATLA will identify the parameters in the template, and infer their types:
- `slot`: string or number 
- `factor`: number
- `num`: number
- `num_list`: number array

## Contributing

Contributions are welcome! If you encounter any issues or have suggestions for improvement, please [submit an issue](https://github.com/eugene-prout/yatla/issues).

## License

This project is licensed under the MIT License - see the [LICENSE](/LICENSE) file for details.

## Acknowledgements

YATLA is developed and maintained by [Eugene Prout](https://www.prout.tech).